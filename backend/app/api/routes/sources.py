"""
IP-SAKTI Sahayak — Sources API Routes
"""
import os
import glob
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

import frontmatter

from app.models.schemas import SourceDocument, SourceListResponse, Jurisdiction
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sources", tags=["Sources"])


@router.get("", response_model=SourceListResponse)
async def list_sources(jurisdiction: Optional[Jurisdiction] = Query(default=None)):
    """List all corpus documents, optionally filtered by jurisdiction."""
    settings = get_settings()
    corpus_dir = settings.CORPUS_DIR
    
    if not os.path.exists(corpus_dir):
        return SourceListResponse(sources=[], total=0, jurisdiction_filter=jurisdiction)
    
    sources = []
    md_files = glob.glob(os.path.join(corpus_dir, "**", "*.md"), recursive=True)
    
    for filepath in md_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
            
            meta = dict(post.metadata)
            doc_jurisdiction = meta.get("jurisdiction", "india")
            
            # Filter by jurisdiction if specified
            if jurisdiction and doc_jurisdiction != jurisdiction.value:
                continue
            
            import hashlib
            doc_id = hashlib.md5(filepath.encode()).hexdigest()[:12]
            
            source = SourceDocument(
                id=doc_id,
                title=meta.get("title", os.path.basename(filepath).replace(".md", "").replace("_", " ").title()),
                jurisdiction=Jurisdiction(doc_jurisdiction),
                category=meta.get("category", "general"),
                statute_type=meta.get("statute_type", ""),
                last_amended=meta.get("last_amended", None),
                official_source=meta.get("official_source", None),
                sections_covered=meta.get("sections_covered", []),
                content_preview=post.content[:200] + "..." if len(post.content) > 200 else post.content
            )
            sources.append(source)
        except Exception as e:
            logger.error(f"Error reading source {filepath}: {e}")
    
    return SourceListResponse(
        sources=sources,
        total=len(sources),
        jurisdiction_filter=jurisdiction
    )


@router.get("/{source_id}")
async def get_source(source_id: str):
    """Get the full content of a specific source document."""
    settings = get_settings()
    corpus_dir = settings.CORPUS_DIR
    
    md_files = glob.glob(os.path.join(corpus_dir, "**", "*.md"), recursive=True)
    
    for filepath in md_files:
        import hashlib
        doc_id = hashlib.md5(filepath.encode()).hexdigest()[:12]
        
        if doc_id == source_id:
            with open(filepath, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
            
            return {
                "id": doc_id,
                "metadata": dict(post.metadata),
                "content": post.content
            }
    
    raise HTTPException(status_code=404, detail="Source document not found")
