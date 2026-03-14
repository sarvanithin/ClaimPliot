from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration settings"""
    # Environment
    ENV: str = "development"
    
    # LLM Settings
    OPENAI_API_KEY: str | None = None
    MARTIAN_API_KEY: str | None = "sk-794db0b5a8af40c3b3f487052fe683c2"
    MARTIAN_BASE_URL: str = "https://api.withmartian.com/v1"
    ANTHROPIC_API_KEY: str | None = None
    DEFAULT_MODEL: str = "openai/gpt-4o-mini"
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
