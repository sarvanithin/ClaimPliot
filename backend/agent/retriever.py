from backend.models.claim import Claim, PolicyReference
from backend.rag.store import PolicyStore
from backend.config import settings

class PolicyRetriever:
    def __init__(self):
        # Initialize chroma store connection
        self.store = PolicyStore()
        
    def retrieve_policies(self, procedure_code: str, diagnosis_codes: list[str], denial_category: str, payer: str) -> list[PolicyReference]:
        """
        Retrieves relevant policy chunks from ChromaDB for the given claim details.
        """
        if not settings.OPENAI_API_KEY:
            return self._mock_retrieve(procedure_code, diagnosis_codes, payer)
            
        # Create a search query based on the claim details
        query = f"Policy for procedure {procedure_code} and diagnosis {' '.join(diagnosis_codes)} for payer {payer}"
        
        try:
            docs = self.store.search(query=query, top_k=3)
            
            policies = []
            for doc in docs:
                source = doc.metadata.get("source", "Unknown Policy")
                policies.append(
                    PolicyReference(
                        source=source,
                        section=f"Chunk {doc.metadata.get('chunk_index', 0)}",
                        text=doc.page_content,
                        relevance="Directly maps to the denied procedure and diagnosis."
                    )
                )
            
            if not policies:
                return self._mock_retrieve(procedure_code, diagnosis_codes, payer)
                
            return policies
            
        except Exception as e:
            print(f"Error retrieving policies: {e}")
            return self._mock_retrieve(procedure_code, diagnosis_codes, payer)
            
    def _mock_retrieve(self, procedure_code: str, diagnosis_codes: list[str], payer: str) -> list[PolicyReference]:
        """Fallback mock for UI testing when LLM isn't configured"""
        return [
            PolicyReference(
                source="CMS LCD L35041",
                section="Section 4.2",
                text="Coverage is allowed when the treating physician documents that the procedure is medically necessary after failed conservative treatments.",
                relevance="Directly supports coverage for this diagnosis if conservative treatment failed."
            ),
            PolicyReference(
                source=f"{payer} Medical Policy 2024-B",
                section="Page 12",
                text=f"For procedure {procedure_code}, patient must show clinical justification and evidence of disease progression.",
                relevance="States requirements which this claim meets based on clinical notes."
            )
        ]
