import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from backend.rag.chunker import chunk_document
from backend.rag.store import PolicyStore

def ingest_policies(policies_dir: str = "backend/data/policies"):
    """
    Reads PDFs from the policies directory, chunks them, and stores them in ChromaDB.
    """
    if not os.path.exists(policies_dir):
        print(f"Directory {policies_dir} does not exist.")
        return

    store = PolicyStore()
    
    pdf_files = list(Path(policies_dir).glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {policies_dir}.")
        return

    total_chunks = 0
    for pdf_path in pdf_files:
        print(f"Processing {pdf_path.name}...")
        try:
            loader = PyPDFLoader(str(pdf_path))
            pages = loader.load()
            
            # Combine pages into a single text for better section-aware chunking
            full_text = "\n".join([page.page_content for page in pages])
            
            # Identify policy type roughly from filename (e.g., "LCD_L35041.pdf")
            policy_type = "LCD" if "LCD" in pdf_path.name.upper() else "NCD"
            
            docs = chunk_document(text=full_text, source_name=pdf_path.stem, policy_type=policy_type)
            store.add_documents(docs)
            total_chunks += len(docs)
            print(f"  -> Added {len(docs)} chunks.")
        except Exception as e:
            print(f"Error processing {pdf_path.name}: {e}")

    print(f"Ingestion complete. Added {total_chunks} total chunks to vector store.")

if __name__ == "__main__":
    ingest_policies()
