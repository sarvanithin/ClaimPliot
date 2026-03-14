# ClaimPilot Architecture & Flow

ClaimPilot is an AI-powered agent designed to automate the process of appealing denied medical insurance claims. By utilizing Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG), it analyzes denial reasons, retrieves relevant medical policies, and drafts customized, evidence-based appeal letters.

## 1. Core Architecture

The system is built on a modern, decoupled architecture:

*   **Frontend (UI):** A React-based Single Page Application (SPA). It provides a clean interface for users (e.g., medical billers) to input claim details (procedure codes, diagnosis codes, payer info, and clinical notes).
*   **Backend (API):** A Python-based FastAPI server. This acts as the orchestration layer, handling communication between the frontend, the AI agent engine, and the vector database.
*   **Agent Engine:** The core intelligence layer built using Langchain. It consists of multiple specialized LLM agents working in sequence. By default, it uses the Martian routing API to intelligently route requests to the best available model (currently configured for `openai/gpt-4o-mini` for optimal token use).
*   **Knowledge Base (RAG):** A ChromaDB vector database. It stores embeddings of complex medical policies (like CMS Local Coverage Determinations or payer-specific guidelines), allowing the agent to retrieve precise policy language relevant to a specific denial.

## 2. The Data Flow (Step-by-Step)

When a user submits a denied claim through the UI, the following flow is triggered:

### Step 1: Input & Initial Processing
1.  The user enters the details of the denied claim (Patient ID, Procedure Code, Diagnosis, Payer, CARC Denial Code, and Clinical Notes) into the React frontend.
2.  The frontend sends a JSON payload to the FastAPI backend's `/api/claims/analyze` endpoint.
3.  FastAPI validates the incoming data using strict Pydantic models (e.g., `Claim`) to ensure all required fields are present and properly formatted.

### Step 2: The Agent Engine Workflow
The backend hands the validated claim data to the `ClaimPilotAgent`, which orchestrates a multi-step pipeline:

#### A. Classification (`DenialClassifier`)
*   **Action:** The claim details are sent to the classification LLM.
*   **Purpose:** The LLM categorizes the root cause of the denial (e.g., "medical_necessity", "coding_error", "timely_filing"). It also extracts a structured reasoning for *why* it chose that category.
*   **Output:** A structured `DenialAnalysis` object.

#### B. Policy Retrieval (`PolicyRetriever`)
*   **Action:** Based on the identified denial category, procedure code, diagnosis, and payer, a semantic search query is generated.
*   **Purpose:** The system queries the ChromaDB vector store to find the top most relevant chunks from embedded medical policy documents.
*   **Output:** A list of `PolicyReference` objects containing exact citations and source texts.

#### C. Drafting the Appeal (`AppealWriter`)
*   **Action:** The original claim data, the classification analysis, and the retrieved policy excerpts are compiled into a comprehensive prompt and sent to the LLM.
*   **Purpose:** The LLM drafts an initial, formal appeal letter. It is instructed to explicitly synthesize the clinical notes with the retrieved policy language to justify medical necessity.

#### D. Self-Critique & Refinement (The loop)
*   **Action:** The initial draft letter, along with the required policy citations, is sent back to the LLM (or a separate critique-focused LLM instance).
*   **Purpose:** The LLM acts as an editor. It reviews the draft specifically to check for "hallucinations" (making sure it didn't invent policy language) and ensures tone and requirements are met.
*   **Output:** A final, refined `AppealLetter` object.

### Step 3: Response & Display
1.  The backend bundles the `DenialAnalysis`, `PolicyReference` list, and final `AppealLetter` into an `AppealResult` payload.
2.  This payload is sent back to the React frontend.
3.  The frontend UI updates, displaying the agent's step-by-step progress, the retrieved policies, and the final generated letter ready for download or copying.

## Summary of the "Accuracy Focus"

ClaimPilot prioritizes accuracy over simple text generation by employing three key strategies throughout its flow:
1.  **Strict Data Contracts:** Using Pydantic to ensure the LLM inputs and outputs conform to expected JSON structures.
2.  **Evidence-Based Context:** Using RAG with ChromaDB ensures the LLM cites *actual* policy rather than its generic training data.
3.  **Self-Correction:** The critique loop forces the agent to verify its own work before presenting it to the user.
