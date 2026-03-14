from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration settings"""
    # Environment
    ENV: str = "development"
    
    # LLM Settings
    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
