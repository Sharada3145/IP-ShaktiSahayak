"""
IP-SAKTI Sahayak — Backend Configuration
"""
import os
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "IP-SAKTI Sahayak"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://ip-shakti-sahayak-frontend.onrender.com"
    ]
    
    # Gemini API
    GEMINI_API_KEY: str = Field(default="", validation_alias="GOOGLE_API_KEY")
    GEMINI_LLM_MODEL: str = "gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"
    GEMINI_EMBEDDING_DIMENSIONS: int = 768
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db")
    CHROMA_COLLECTION_NAME: str = "legal_corpus"
    
    # RAG Settings
    RAG_TOP_K: int = 8
    RAG_SIMILARITY_THRESHOLD: float = 0.65
    RAG_CHUNK_SIZE: int = 1024
    RAG_CHUNK_OVERLAP: int = 128
    
    # Corpus
    CORPUS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "corpus")
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = 30
    
    class Config:
        env_file = (".env", "../.env")
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
