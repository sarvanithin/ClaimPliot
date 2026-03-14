from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def get_policy_chunker() -> RecursiveCharacterTextSplitter:
    """
    Returns a text splitter configured for medical policy documents.
    Policy documents often have section headers (Markdown or typical PDF structure).
    We use separators that respect paragraph and sentence boundaries to avoid
    cutting off important medical context.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=750,      # Slightly larger chunks to capture full context
        chunk_overlap=150,   # Overlap to ensure cross-chunk context isn't lost
        length_function=len,
        separators=["\n\n", "\n", ".", " ", ""],
        is_separator_regex=False,
    )

def chunk_document(text: str, source_name: str, policy_type: str = "LCD") -> list[Document]:
    """
    Chunks a single document text and attaches metadata.
    """
    chunker = get_policy_chunker()
    chunks = chunker.split_text(text)
    
    documents = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            page_content=chunk,
            metadata={
                "source": source_name,
                "type": policy_type,
                "chunk_index": i
            }
        )
        documents.append(doc)
        
    return documents
