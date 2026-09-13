"""
IP-SAKTI Sahayak — FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.routes import chat, tools, sources
from app.models.schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    settings = get_settings()
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Run corpus ingestion on startup
    try:
        from app.ingestion.ingest import CorpusIngestor
        ingestor = CorpusIngestor()
        stats = ingestor.ingest_all()
        logger.info(f"📚 Corpus ingestion: {stats['processed']} docs, {stats['chunks_added']} chunks")
    except Exception as e:
        logger.warning(f"⚠️ Corpus ingestion skipped: {e}")
    
    yield
    
    logger.info("👋 Shutting down IP-SAKTI Sahayak")


# Create FastAPI app
settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "A multilingual, RAG-based AI assistant for Intellectual Property "
        "and regulatory guidance in Ayurveda, across national and international regimes."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(tools.router)
app.include_router(sources.router)


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    corpus_docs = 0
    vector_ready = False
    llm_ready = False
    
    try:
        from app.services.rag_service import RAGService
        rag = RAGService.get_instance()
        corpus_docs = rag.get_document_count()
        vector_ready = rag.is_ready()
    except Exception:
        pass
    
    try:
        from app.services.llm_service import LLMService
        llm = LLMService.get_instance()
        llm_ready = llm.is_ready()
    except Exception:
        pass
    
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        corpus_documents=corpus_docs,
        vector_store_ready=vector_ready,
        llm_ready=llm_ready
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "RAG-based AI assistant for IP guidance in Ayurveda",
        "docs": "/docs",
        "health": "/api/health"
    }
