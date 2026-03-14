import json
import os
from fastapi import APIRouter, HTTPException
from backend.models.claim import Claim, AppealResult
from backend.agent.engine import ClaimPilotAgent

router = APIRouter()
agent = ClaimPilotAgent()

@router.post("/claims/analyze", response_model=AppealResult)
async def analyze_claim(claim: Claim):
    """
    Process a denied claim through the agent engine to generate an appeal.
    """
    try:
        result = agent.process_claim(claim)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/denial-codes")
async def get_denial_codes():
    """
    Returns a list of all supported CARC denial codes.
    """
    try:
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "denial_codes.json")
        with open(data_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@router.get("/demo-claims")
async def get_demo_claims(test_case_id: str = None):
    """
    Returns a list of pre-built demo scenarios or a specific one.
    """
    try:
        # Reusing evaluation test cases for demos
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "evaluation", "test_cases.json")
        with open(data_path, "r") as f:
            cases = json.load(f)
            
        if test_case_id:
            for case in cases:
                if case.get("id") == test_case_id:
                    return case
            raise HTTPException(status_code=404, detail="Demo scenario not found")
        
        return cases
    except FileNotFoundError:
        return []

@router.get("/health")
async def health_check():
    """
    Check the health of the system.
    """
    return {"status": "ok", "message": "ClaimPilot API is running", "model_configured": bool(os.getenv("OPENAI_API_KEY"))}
