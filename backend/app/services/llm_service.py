"""
IP-SAKTI Sahayak — LLM Service (Gemini)
"""
import google.generativeai as genai
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
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_LLM_MODEL,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                top_p=0.85,
                top_k=40,
                max_output_tokens=4096,
            ),
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
            ]
        )
        logger.info(f"LLMService initialized with model: {settings.GEMINI_LLM_MODEL}")
    
    @classmethod
    def get_instance(cls) -> "LLMService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a response using the Gemini model."""
        try:
            chat = self.model.start_chat(history=[])
            # Combine system prompt with user prompt for Gemini
            full_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
            response = chat.send_message(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            raise
    
    async def generate_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        """Generate a streaming response using the Gemini model."""
        try:
            chat = self.model.start_chat(history=[])
            full_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
            response = chat.send_message(full_prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Error in streaming LLM response: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Check if the LLM service is ready."""
        try:
            response = self.model.generate_content("Say 'ready' in one word.")
            return bool(response.text)
        except Exception:
            return False
