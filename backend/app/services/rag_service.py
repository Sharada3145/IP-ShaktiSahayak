"""
IP-SAKTI Sahayak — RAG Service (Core Pipeline)
"""
import chromadb
from typing import Optional
import logging
import uuid
import re

from app.core.config import get_settings
from app.core.prompts import (
    SYSTEM_PROMPT_INDIA, SYSTEM_PROMPT_INTERNATIONAL,
    RAG_QUERY_PROMPT
)
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.citation_service import CitationService
from app.models.schemas import (
    ChatRequest, ChatResponse, Citation,
    Jurisdiction, Confidence
)

logger = logging.getLogger(__name__)


class RAGService:
    """Core RAG pipeline: embed query → retrieve from ChromaDB → augment prompt → generate answer."""
    
    _instance: Optional["RAGService"] = None
    
    def __init__(self):
        settings = get_settings()
        self.embedding_service = EmbeddingService.get_instance()
        self.llm_service = LLMService.get_instance()
        self.citation_service = CitationService()
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.chroma_client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.top_k = settings.RAG_TOP_K
        self.similarity_threshold = settings.RAG_SIMILARITY_THRESHOLD
        
        logger.info(f"RAGService initialized. Collection has {self.collection.count()} documents.")
    
    @classmethod
    def get_instance(cls) -> "RAGService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def query(self, request: ChatRequest) -> ChatResponse:
        """
        Main RAG query pipeline.
        1. Generate query embedding
        2. Retrieve relevant chunks from ChromaDB (filtered by jurisdiction)
        3. Construct augmented prompt
        4. Generate answer via LLM
        5. Extract citations
        6. Return structured response
        """
        session_id = request.session_id or str(uuid.uuid4())
        
        # Step 1: Generate query embedding
        query_embedding = self.embedding_service.embed_query(request.query)
        
        # Step 2: Retrieve relevant chunks from ChromaDB
        where_filter = {"jurisdiction": request.jurisdiction.value}
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        # Check if we have sufficient context
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        
        if not documents:
            return self._insufficient_context_response(request, session_id)
        
        # Filter by similarity threshold (ChromaDB cosine distance: lower = more similar)
        filtered_docs = []
        filtered_metas = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            # Cosine distance: 0 = identical, 2 = opposite. Convert to similarity.
            similarity = 1 - (dist / 2)
            if similarity >= self.similarity_threshold:
                filtered_docs.append(doc)
                filtered_metas.append(meta)
        
        if not filtered_docs:
            return self._insufficient_context_response(request, session_id)
        
        # Step 3: Build context string from retrieved chunks
        context_parts = []
        for i, (doc, meta) in enumerate(zip(filtered_docs, filtered_metas)):
            source_info = f"[Source {i+1}: {meta.get('title', 'Unknown')} — {meta.get('section', 'General')}]"
            context_parts.append(f"{source_info}\n{doc}")
        
        context_string = "\n\n---\n\n".join(context_parts)
        
        # Step 4: Select system prompt based on jurisdiction
        system_prompt = (
            SYSTEM_PROMPT_INDIA if request.jurisdiction == Jurisdiction.INDIA
            else SYSTEM_PROMPT_INTERNATIONAL
        )
        
        # Build the user prompt with context
        user_prompt = RAG_QUERY_PROMPT.format(
            context=context_string,
            query=request.query
        )
        
        # Step 5: Generate answer via LLM
        answer_text = self.llm_service.generate(system_prompt, user_prompt)
        
        # Step 6: Extract citations
        citations = self.citation_service.extract_citations(
            answer_text, filtered_metas, request.jurisdiction
        )
        
        # Determine overall confidence
        overall_confidence = self._determine_confidence(filtered_docs, distances)
        
        # Extract related queries from the answer (if the LLM included them)
        related_queries = self._extract_related_queries(answer_text)
        
        return ChatResponse(
            answer=answer_text,
            citations=citations,
            confidence=overall_confidence,
            jurisdiction=request.jurisdiction,
            related_queries=related_queries,
            session_id=session_id
        )
    
    def _insufficient_context_response(self, request: ChatRequest, session_id: str) -> ChatResponse:
        """Generate a safe abstention response when context is insufficient."""
        jurisdiction_label = "Indian national" if request.jurisdiction == Jurisdiction.INDIA else "international"
        
        return ChatResponse(
            answer=(
                f"I don't have sufficient information in my current knowledge base to answer this question "
                f"accurately within the {jurisdiction_label} legal framework.\n\n"
                f"**Recommendation:** Please consult a qualified IP attorney or registered patent agent "
                f"who specializes in {jurisdiction_label} IP law and AYUSH/traditional medicine regulations.\n\n"
                f"You can also try:\n"
                f"- Rephrasing your question with more specific details\n"
                f"- Switching the jurisdiction toggle if your question relates to the other regime\n"
                f"- Using the Formulation Classifier to determine the regulatory category of your product"
            ),
            citations=[],
            confidence=Confidence.LOW,
            jurisdiction=request.jurisdiction,
            related_queries=[
                "What types of IP protection are available for Ayurvedic products?",
                "How does the TKDL prevent patent misappropriation?",
                "What is the difference between classical and proprietary Ayurvedic medicines?"
            ],
            session_id=session_id
        )
    
    def _determine_confidence(self, documents: list, distances: list) -> Confidence:
        """Determine overall confidence based on retrieval quality."""
        if not distances:
            return Confidence.LOW
        
        # Average similarity of top results
        avg_similarity = 1 - (sum(distances[:3]) / (2 * min(3, len(distances))))
        
        if avg_similarity >= 0.82:
            return Confidence.HIGH
        elif avg_similarity >= 0.70:
            return Confidence.MEDIUM
        else:
            return Confidence.LOW
    
    def _extract_related_queries(self, answer: str) -> list[str]:
        """Extract related/follow-up questions from the LLM response."""
        related = []
        # Look for the "Related Topics" section
        pattern = r"🔗\s*\*?\*?Related Topics\*?\*?:?\s*(.*?)(?:\n\n|⚖️|$)"
        match = re.search(pattern, answer, re.DOTALL)
        if match:
            lines = match.group(1).strip().split("\n")
            for line in lines:
                cleaned = re.sub(r"^[\d\-\*•]+\.?\s*", "", line.strip())
                if cleaned and len(cleaned) > 10:
                    related.append(cleaned)
        return related[:3]
    
    def get_document_count(self) -> int:
        """Return the number of documents in the vector store."""
        return self.collection.count()
    
    def is_ready(self) -> bool:
        """Check if the RAG service is operational."""
        try:
            return self.collection.count() >= 0
        except Exception:
            return False
