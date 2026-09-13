"""
IP-SAKTI Sahayak — Embedding Service (Gemini text-embedding-004)
"""
import google.generativeai as genai
from typing import Optional
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Wrapper around Google Gemini Embedding API."""
    
    _instance: Optional["EmbeddingService"] = None
    
    def __init__(self):
        settings = get_settings()
        api_key = settings.GEMINI_API_KEY.strip().strip('"\'')
        genai.configure(api_key=api_key)
        self.model_name = settings.GEMINI_EMBEDDING_MODEL
        self.dimensions = settings.GEMINI_EMBEDDING_DIMENSIONS
        logger.info(f"EmbeddingService initialized with model: {self.model_name}")
    
    @classmethod
    def get_instance(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query text."""
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_query"
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise
    
    def embed_document(self, text: str) -> list[float]:
        """Generate embedding for a single document text."""
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_document"
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Error generating document embedding: {e}")
            raise
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple document texts (batched)."""
        embeddings = []
        batch_size = 100  # Gemini API batch limit
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                result = genai.embed_content(
                    model=self.model_name,
                    content=batch,
                    task_type="retrieval_document"
                )
                embeddings.extend(result["embedding"])
            except Exception as e:
                logger.error(f"Error in batch embedding (batch {i // batch_size}): {e}")
                raise
        
        return embeddings
