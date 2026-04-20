"""Lightweight V1 appeal endpoint that works without langchain.

Uses deterministic classification + LLM-powered appeal generation via
Withmartian API (OpenAI-compatible). Falls back to templates if API unavailable.
"""

from __future__ import annotations

import json
import os
from datetime import datetime

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

from backend.config import settings

v1_fallback_router = APIRouter()

# ── CARC code classification map ──────────────────────────────────────

_CARC_CATEGORIES = {
    "CO-4": ("administrative", "coding_error"),
    "CO-11": ("clinical", "coding_error"),
    "CO-16": ("administrative", "documentation"),
    "CO-18": ("administrative", "coding_error"),
    "CO-22": ("administrative", "coordination"),
    "CO-27": ("administrative", "coverage"),
    "CO-29": ("administrative", "timely_filing"),
    "CO-50": ("clinical", "medical_necessity"),
    "CO-96": ("clinical", "coverage"),
    "CO-97": ("clinical", "coding_error"),
    "CO-109": ("clinical", "coverage"),
    "CO-151": ("clinical", "documentation"),
    "CO-167": ("clinical", "coverage"),
    "CO-197": ("administrative", "auth_missing"),
    "CO-204": ("clinical", "coverage"),
    "CO-236": ("administrative", "coding_error"),
    "PR-1": ("administrative", "patient_responsibility"),
    "PR-2": ("administrative", "patient_responsibility"),
    "PR-3": ("administrative", "patient_responsibility"),
}

_CARC_DESCRIPTIONS = {
    "CO-4": "The procedure code is inconsistent with the modifier used or a required modifier is missing.",
    "CO-11": "The diagnosis is inconsistent with the procedure.",
    "CO-16": "Claim/service lacks information or has submission/billing error(s).",
    "CO-18": "Exact duplicate claim/service.",
    "CO-22": "This care may be covered by another payer per coordination of benefits.",
    "CO-27": "Expenses incurred after coverage terminated.",
    "CO-29": "The time limit for filing has expired.",
    "CO-50": "These are non-covered services because this is not deemed a medical necessity.",
    "CO-96": "Non-covered charge(s).",
    "CO-97": "The benefit for this service is included in the allowance/payment for another service.",
    "CO-109": "Claim/service not covered by this payer/contractor.",
    "CO-151": "Payment adjusted because the payer deems the information submitted does not support this level of service.",
    "CO-167": "This (these) diagnosis(es) is (are) not covered.",
    "CO-197": "Precertification/authorization/notification absent.",
    "CO-204": "This service/equipment/drug is not covered under the patient's current benefit plan.",
    "CO-236": "This procedure or procedure/modifier combination is not compatible with another procedure or procedure/modifier combination provided on the same day.",
}

_ROOT_CAUSES = {
    "medical_necessity": "Payer requires additional clinical documentation demonstrating that the service was medically necessary. This often occurs when the diagnosis codes do not sufficiently support the procedure performed.",
    "coding_error": "The procedure code, modifier, or diagnosis code combination does not meet payer editing rules. Review coding for accuracy.",
    "auth_missing": "Prior authorization was required for this service but was not obtained or not on file with the payer.",
    "timely_filing": "The claim was submitted after the payer's timely filing deadline.",
    "documentation": "The payer requires additional documentation to process this claim. The submitted information was insufficient.",
    "coverage": "The service is not covered under the patient's current benefit plan or the diagnosis is not a covered condition.",
    "coordination": "Another payer may be primary. Coordination of benefits needs to be verified.",
    "patient_responsibility": "The amount is the patient's responsibility (deductible, coinsurance, or copay).",
}

_APPEAL_STRATEGIES = {
    "medical_necessity": "Cite relevant CMS LCD/NCD policies and payer medical policy. Include clinical notes documenting severity, failed conservative treatment, and clinical decision-making rationale.",
    "coding_error": "Review and correct CPT/ICD-10 coding. Include documentation supporting the code selection and any required modifiers.",
    "auth_missing": "Submit proof of prior authorization if obtained. If not required per policy, cite the applicable coverage determination.",
    "timely_filing": "Provide proof of original timely submission (electronic confirmation, postal receipt) and request reconsideration.",
    "documentation": "Compile and submit all required clinical documentation including operative reports, clinical notes, and test results.",
    "coverage": "Reference the specific benefit plan language and demonstrate that the service meets coverage criteria.",
    "coordination": "Verify primary/secondary payer status and resubmit with correct coordination of benefits information.",
    "patient_responsibility": "Verify patient responsibility amounts against the benefit plan. Appeal if the calculation appears incorrect.",
}

# ── Request/Response models ───────────────────────────────────────────

class Claim(BaseModel):
    patient_id: str
    procedure_code: str
    diagnosis_codes: List[str]
    payer: str
    denial_code: str
    denial_reason: str
    date_of_service: str
    provider_name: str
    clinical_notes: Optional[str] = None


class PolicyReference(BaseModel):
    source: str
    section: str
    text: str
    relevance: str


class DenialAnalysis(BaseModel):
    track: str
    denial_category: str
    denial_code: str
    denial_description: str
    root_cause: str
    appeal_strategy: str
    relevant_policies: List[PolicyReference] = Field(default_factory=list)
    success_probability: str


class AppealLetter(BaseModel):
    subject_line: str
    date: str
    payer_address: str
    re_line: str
    opening: str
    medical_necessity: str
    policy_citations: str
    conclusion: str
    attachments_needed: List[str] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)
    success_score_1_to_100: int = 50
    full_text: str


class AppealResult(BaseModel):
    analysis: DenialAnalysis
    policies: List[PolicyReference]
    appeal: AppealLetter


# ── Classification ────────────────────────────────────────────────────

def _classify(claim: Claim) -> DenialAnalysis:
    track, category = _CARC_CATEGORIES.get(claim.denial_code, ("clinical", "medical_necessity"))
    description = _CARC_DESCRIPTIONS.get(claim.denial_code, claim.denial_reason)
    root_cause = _ROOT_CAUSES.get(category, _ROOT_CAUSES["medical_necessity"])
    strategy = _APPEAL_STRATEGIES.get(category, _APPEAL_STRATEGIES["medical_necessity"])

    # Estimate success probability based on category
    high_success = {"coding_error", "auth_missing", "documentation", "coordination"}
    low_success = {"timely_filing", "patient_responsibility"}
    if category in high_success:
        probability = "high"
    elif category in low_success:
        probability = "low"
    else:
        probability = "medium"

    return DenialAnalysis(
        track=track,
        denial_category=category,
        denial_code=claim.denial_code,
        denial_description=description,
        root_cause=root_cause,
        appeal_strategy=strategy,
        relevant_policies=[],
        success_probability=probability,
    )


# ── Policy retrieval (deterministic) ─────────────────────────────────

def _retrieve_policies(claim: Claim, analysis: DenialAnalysis) -> list[PolicyReference]:
    policies = []

    if analysis.denial_category == "medical_necessity":
        policies.append(PolicyReference(
            source="CMS LCD L35041",
            section="Section 4.2 — Medical Necessity Criteria",
            text=f"Coverage is provided for procedure {claim.procedure_code} when the treating physician documents that the service is medically necessary, conservative treatments have been attempted and failed, and the patient's condition warrants intervention.",
            relevance="Establishes the medical necessity standard that this appeal must meet.",
        ))
        policies.append(PolicyReference(
            source=f"{claim.payer} Medical Policy",
            section="Coverage Determination Guidelines",
            text=f"For diagnosis codes {', '.join(claim.diagnosis_codes)}, the payer requires documentation of clinical progression, failed conservative treatment, and physician attestation of necessity.",
            relevance="Payer-specific requirements for the submitted diagnosis codes.",
        ))
    elif analysis.denial_category == "coding_error":
        policies.append(PolicyReference(
            source="AMA CPT Guidelines",
            section="Modifier Usage",
            text=f"CPT code {claim.procedure_code} may be reported with appropriate modifiers when distinct services are performed. Documentation must support each separately identifiable service.",
            relevance="Supports correct use of the procedure code and modifiers.",
        ))
    elif analysis.denial_category == "auth_missing":
        policies.append(PolicyReference(
            source=f"{claim.payer} Prior Authorization Policy",
            section="Authorization Requirements",
            text=f"Prior authorization is required for procedure {claim.procedure_code}. Retrospective authorization may be granted within 72 hours for emergent/urgent services.",
            relevance="Identifies the authorization requirement and potential exception for urgent cases.",
        ))
    else:
        policies.append(PolicyReference(
            source=f"{claim.payer} Provider Manual",
            section="Claims Filing Requirements",
            text=f"Claims must meet all submission requirements including correct coding, supporting documentation, and timely filing within {claim.payer}'s specified deadline.",
            relevance="General requirements applicable to this denial category.",
        ))

    return policies


# ── Appeal generation ─────────────────────────────────────────────────

def _generate_appeal(claim: Claim, analysis: DenialAnalysis, policies: list[PolicyReference]) -> AppealLetter:
    today = datetime.utcnow().strftime("%m/%d/%Y")
    policy_text = "\n".join(f"  - [{p.source}, {p.section}]: {p.text}" for p in policies)
    dx_str = ", ".join(claim.diagnosis_codes)

    # Build the appeal body based on denial category
    if analysis.denial_category == "medical_necessity":
        body = f"""The claim was denied under {claim.denial_code}: "{analysis.denial_description}"

However, the clinical documentation clearly establishes medical necessity for CPT {claim.procedure_code} with diagnoses {dx_str}.

CLINICAL JUSTIFICATION:
{claim.clinical_notes or 'Clinical documentation on file supports the medical necessity of this service.'}

Per the applicable coverage criteria (referenced below), this patient meets all requirements:
{policy_text}

The patient's documented condition, treatment history, and clinical presentation all demonstrate that this service was medically necessary and appropriate. We respectfully request that the claim be reprocessed for payment."""

    elif analysis.denial_category == "auth_missing":
        body = f"""The claim was denied under {claim.denial_code} for missing prior authorization.

We have reviewed our records and believe that either:
1. Prior authorization was obtained (reference attached), or
2. The service qualified for retrospective authorization due to clinical urgency.

Clinical context supporting urgency:
{claim.clinical_notes or 'Patient presentation required timely intervention.'}

We request that the claim be reconsidered based on the enclosed documentation."""

    elif analysis.denial_category == "coding_error":
        body = f"""The claim was denied under {claim.denial_code}: "{analysis.denial_description}"

We have reviewed the coding for CPT {claim.procedure_code} with diagnoses {dx_str} and confirm that the codes accurately reflect the services provided.

{claim.clinical_notes or 'The operative report and clinical documentation support the code selection.'}

Per coding guidelines:
{policy_text}

We request that the claim be reprocessed with the submitted codes."""

    else:
        body = f"""The claim was denied under {claim.denial_code}: "{analysis.denial_description}"

We are submitting this appeal with additional documentation to address the denial reason.

{claim.clinical_notes or 'Supporting documentation is enclosed.'}

Referenced policies:
{policy_text}

We respectfully request reconsideration of this claim."""

    full_text = f"""Date: {today}

To: {claim.payer} Claims Review Department
Re: Appeal of Claim for Patient {claim.patient_id}, DOS {claim.date_of_service}
Provider: {claim.provider_name}
Procedure: CPT {claim.procedure_code}
Diagnosis: {dx_str}

Dear Appeals Review Committee,

I am writing to formally appeal the denial of the above-referenced claim.

{body}

Please contact our office if additional information is needed.

Sincerely,
{claim.provider_name}
"""

    # Determine attachments and missing evidence
    attachments = ["Clinical Notes", "Provider Letter of Medical Necessity"]
    missing = []

    if analysis.denial_category == "medical_necessity":
        attachments.extend(["Operative Report", "Treatment History"])
        if not claim.clinical_notes:
            missing.append("Detailed clinical notes documenting medical necessity")
        missing.append("Documentation of failed conservative treatment attempts")
    elif analysis.denial_category == "auth_missing":
        attachments = ["Prior Authorization Reference", "Clinical Urgency Documentation"]
    elif analysis.denial_category == "coding_error":
        attachments = ["Operative Report", "Coding Rationale"]

    # Score: higher for categories that commonly overturn
    score_map = {"coding_error": 75, "auth_missing": 70, "documentation": 65, "medical_necessity": 60, "coverage": 45, "timely_filing": 30}
    score = score_map.get(analysis.denial_category, 50)
    if claim.clinical_notes:
        score = min(95, score + 10)

    return AppealLetter(
        subject_line=f"Appeal — Claim for Patient {claim.patient_id}, {claim.denial_code}",
        date=today,
        payer_address=f"{claim.payer} Claims Review Department",
        re_line=f"Re: Appeal of Claim for Patient {claim.patient_id}, DOS {claim.date_of_service}",
        opening="Dear Appeals Review Committee,",
        medical_necessity=body.split("\n")[0] if analysis.track == "clinical" else "N/A — Administrative issue.",
        policy_citations=policy_text,
        conclusion="We respectfully request that this claim be reconsidered and reprocessed for payment.",
        attachments_needed=attachments,
        missing_evidence=missing,
        success_score_1_to_100=score,
        full_text=full_text,
    )


# ── LLM-powered appeal via Withmartian API ───────────────────────────

async def _llm_generate_appeal(
    claim: Claim, analysis: DenialAnalysis, policies: list[PolicyReference]
) -> AppealLetter | None:
    """Generate appeal letter using Withmartian (OpenAI-compatible) API.
    Returns None if API is unavailable, so caller can fall back to templates."""
    api_key = settings.MARTIAN_API_KEY
    if not api_key:
        return None

    policy_text = "\n".join(f"- [{p.source}, {p.section}]: {p.text}" for p in policies)
    dx_str = ", ".join(claim.diagnosis_codes)
    today = datetime.utcnow().strftime("%m/%d/%Y")

    system_prompt = """You are a medical billing appeal specialist. Generate professional,
persuasive appeal letters for denied insurance claims. Your letters should:
- Reference specific CARC denial codes and their implications
- Cite relevant CMS/payer policies
- Include clinical justification from the provided notes
- Follow standard appeal letter format
- Be concise but thorough

Respond with ONLY the appeal letter text, no JSON wrapping or explanations."""

    user_prompt = f"""Generate an appeal letter for this denied claim:

CLAIM DETAILS:
- Patient: {claim.patient_id}
- Provider: {claim.provider_name}
- Date of Service: {claim.date_of_service}
- Procedure: CPT {claim.procedure_code}
- Diagnoses: {dx_str}
- Payer: {claim.payer}
- Denial Code: {claim.denial_code}
- Denial Reason: {analysis.denial_description}

ANALYSIS:
- Track: {analysis.track}
- Category: {analysis.denial_category}
- Root Cause: {analysis.root_cause}
- Strategy: {analysis.appeal_strategy}

CLINICAL NOTES:
{claim.clinical_notes or 'No additional clinical notes provided.'}

RELEVANT POLICIES:
{policy_text}

Write a formal appeal letter addressed to {claim.payer} Claims Review Department."""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.MARTIAN_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.MARTIAN_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1500,
                },
            )
            response.raise_for_status()
            data = response.json()
            full_text = data["choices"][0]["message"]["content"]

        # Determine attachments and missing evidence based on category
        attachments = ["Clinical Notes", "Provider Letter of Medical Necessity"]
        missing = []
        if analysis.denial_category == "medical_necessity":
            attachments.extend(["Operative Report", "Treatment History"])
            if not claim.clinical_notes:
                missing.append("Detailed clinical notes documenting medical necessity")
            missing.append("Documentation of failed conservative treatment attempts")
        elif analysis.denial_category == "auth_missing":
            attachments = ["Prior Authorization Reference", "Clinical Urgency Documentation"]
        elif analysis.denial_category == "coding_error":
            attachments = ["Operative Report", "Coding Rationale"]

        score_map = {"coding_error": 80, "auth_missing": 75, "documentation": 70, "medical_necessity": 65, "coverage": 50, "timely_filing": 35}
        score = score_map.get(analysis.denial_category, 55)
        if claim.clinical_notes:
            score = min(95, score + 10)

        return AppealLetter(
            subject_line=f"Appeal — Claim for Patient {claim.patient_id}, {claim.denial_code}",
            date=today,
            payer_address=f"{claim.payer} Claims Review Department",
            re_line=f"Re: Appeal of Claim for Patient {claim.patient_id}, DOS {claim.date_of_service}",
            opening="Dear Appeals Review Committee,",
            medical_necessity="See full letter for clinical justification." if analysis.track == "clinical" else "N/A — Administrative issue.",
            policy_citations=policy_text,
            conclusion="We respectfully request that this claim be reconsidered and reprocessed for payment.",
            attachments_needed=attachments,
            missing_evidence=missing,
            success_score_1_to_100=score,
            full_text=full_text,
        )
    except Exception as e:
        print(f"[ClaimPilot] LLM appeal generation failed: {e}")
        return None


# ── Endpoints ─────────────────────────────────────────────────────────

@v1_fallback_router.post("/claims/analyze", response_model=AppealResult)
async def analyze_claim(claim: Claim):
    """Process a denied claim and generate an appeal.
    Uses LLM (Withmartian) if available, falls back to templates."""
    analysis = _classify(claim)
    policies = _retrieve_policies(claim, analysis)

    # Try LLM-powered appeal first
    appeal = await _llm_generate_appeal(claim, analysis, policies)
    if appeal is None:
        # Fall back to template-based
        appeal = _generate_appeal(claim, analysis, policies)

    return AppealResult(analysis=analysis, policies=policies, appeal=appeal)


@v1_fallback_router.get("/denial-codes")
async def get_denial_codes():
    """Returns supported CARC denial codes."""
    return [{"code": k, "description": v} for k, v in _CARC_DESCRIPTIONS.items()]


@v1_fallback_router.get("/demo-claims")
async def get_demo_claims():
    """Returns pre-built demo scenarios."""
    try:
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "evaluation", "test_cases.json")
        with open(data_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


@v1_fallback_router.get("/health")
async def health_check():
    has_llm = bool(settings.MARTIAN_API_KEY)
    return {"status": "ok", "message": "ClaimPilot API is running", "model_configured": has_llm, "mode": "llm" if has_llm else "template"}
