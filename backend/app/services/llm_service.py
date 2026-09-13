"""
IP-SAKTI Sahayak — LLM Service (Gemini)
"""
from google import genai
from google.genai import types
from typing import Optional, AsyncGenerator
import logging
import json

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    """Wrapper around Google Gemini LLM API."""
    
    _instance: Optional["LLMService"] = None
    
    def __init__(self):
        settings = get_settings()
        api_key = settings.GEMINI_API_KEY.strip().strip('"\'')
        self.client = genai.Client(api_key=api_key)
        self.model_name = settings.GEMINI_LLM_MODEL

        self.generation_config = types.GenerateContentConfig(
            temperature=0.3,
            top_p=0.85,
            top_k=40,
            max_output_tokens=4096,
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="BLOCK_ONLY_HIGH",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="BLOCK_ONLY_HIGH",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="BLOCK_ONLY_HIGH",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_ONLY_HIGH",
                ),
            ],
        )
        logger.info(f"LLMService initialized with model: {self.model_name}")
    
    @classmethod
    def get_instance(cls) -> "LLMService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a response using the Gemini model."""
        try:
            # Combine system prompt with user prompt for Gemini
            full_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=self.generation_config,
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            raise
    
    async def generate_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        """Generate a streaming response using the Gemini model."""
        try:
            full_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
            
            for chunk in self.client.models.generate_content_stream(
                model=self.model_name,
                contents=full_prompt,
                config=self.generation_config,
            ):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Error in streaming LLM response: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Check if the LLM service is ready."""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Say 'ready' in one word.",
            )
            return bool(response.text)
        except Exception:
            return False
