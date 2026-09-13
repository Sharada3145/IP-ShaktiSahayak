"""
IP-SAKTI Sahayak — Chat API Routes
"""
import uuid
import logging
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse
import json
import asyncio

from app.models.schemas import ChatRequest, ChatResponse, Jurisdiction
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main RAG query endpoint.
    Accepts a question + jurisdiction and returns a cited answer.
    """
    try:
        rag_service = RAGService.get_instance()
        response = rag_service.query(request)
        return response
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming RAG query endpoint using Server-Sent Events (SSE).
    """
    async def event_generator():
        try:
            rag_service = RAGService.get_instance()
            # For streaming, we first do retrieval, then stream the LLM response
            response = rag_service.query(request)
            
            # Stream the answer in chunks
            words = response.answer.split(" ")
            buffer = ""
            for i, word in enumerate(words):
                buffer += word + " "
                if i % 5 == 0:  # Send every 5 words
                    yield {
                        "event": "message",
                        "data": json.dumps({"chunk": buffer, "done": False})
                    }
                    buffer = ""
                    await asyncio.sleep(0.02)
            
            # Send remaining buffer
            if buffer:
                yield {
                    "event": "message",
                    "data": json.dumps({"chunk": buffer, "done": False})
                }
            
            # Send final event with citations and metadata
            yield {
                "event": "message",
                "data": json.dumps({
                    "chunk": "",
                    "done": True,
                    "citations": [c.model_dump() for c in response.citations],
                    "confidence": response.confidence.value,
                    "jurisdiction": response.jurisdiction.value,
                    "related_queries": response.related_queries,
                    "disclaimer": response.disclaimer,
                    "session_id": response.session_id
                })
            }
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    return EventSourceResponse(event_generator())
