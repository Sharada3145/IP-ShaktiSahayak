"""
IP-SAKTI Sahayak — Corpus Ingestion Pipeline
Reads Markdown files with YAML frontmatter, chunks them, embeds, and stores in ChromaDB.
"""
import os
import glob
import hashlib
import logging
from typing import Optional

import frontmatter
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class CorpusIngestor:
    """Ingests the curated legal corpus into ChromaDB."""
    
    def __init__(self):
        settings = get_settings()
        self.corpus_dir = settings.CORPUS_DIR
        self.embedding_service = EmbeddingService.get_instance()
        
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.chroma_client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.RAG_CHUNK_SIZE,
            chunk_overlap=settings.RAG_CHUNK_OVERLAP,
            separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", ". ", " "],
            length_function=len,
        )
        
        logger.info(f"CorpusIngestor initialized. Corpus dir: {self.corpus_dir}")
    
    def ingest_all(self, force: bool = False) -> dict:
        """
        Ingest all corpus documents from the corpus directory.
        
        Args:
            force: If True, re-ingest all documents even if they already exist.
        
        Returns:
            Summary dict with counts of processed, skipped, and errored documents.
        """
        stats = {"processed": 0, "skipped": 0, "errors": 0, "chunks_added": 0}
        
        if not os.path.exists(self.corpus_dir):
            logger.warning(f"Corpus directory not found: {self.corpus_dir}")
            os.makedirs(self.corpus_dir, exist_ok=True)
            return stats
        
        # Find all Markdown files recursively
        md_files = glob.glob(os.path.join(self.corpus_dir, "**", "*.md"), recursive=True)
        logger.info(f"Found {len(md_files)} corpus documents")
        
        for filepath in md_files:
            try:
                chunks_added = self._ingest_file(filepath, force=force)
                if chunks_added > 0:
                    stats["processed"] += 1
                    stats["chunks_added"] += chunks_added
                    logger.info(f"✅ Ingested: {os.path.basename(filepath)} ({chunks_added} chunks)")
                else:
                    stats["skipped"] += 1
            except Exception as e:
                stats["errors"] += 1
                logger.error(f"❌ Error ingesting {filepath}: {e}")
        
        logger.info(f"Ingestion complete: {stats}")
        return stats
    
    def _ingest_file(self, filepath: str, force: bool = False) -> int:
        """
        Ingest a single Markdown file into ChromaDB.
        
        Returns:
            Number of chunks added (0 if skipped).
        """
        # Read and parse frontmatter
        with open(filepath, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
        
        metadata = dict(post.metadata)
        content = post.content
        
        if not content.strip():
            logger.warning(f"Empty content in {filepath}, skipping")
            return 0
        
        # Generate document ID from filepath
        doc_id = hashlib.md5(filepath.encode()).hexdigest()[:12]
        content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
        
        # Check if already ingested (unless force)
        if not force:
            existing = self.collection.get(
                where={"doc_id": doc_id},
                limit=1
            )
            if existing and existing["ids"]:
                # Check if content has changed
                existing_metadatas = existing.get("metadatas", [])
                if existing_metadatas and existing_metadatas[0]:
                    stored_hash = existing_metadatas[0].get("content_hash")
                    if stored_hash == content_hash:
                        return 0

                # Content changed (or no hash was stored), delete old chunks before re-ingesting
                self.collection.delete(where={"doc_id": doc_id})
        
        # Determine jurisdiction from filepath or metadata
        jurisdiction = metadata.get("jurisdiction", "")
        if not jurisdiction:
            if "india" in filepath.lower():
                jurisdiction = "india"
            elif "international" in filepath.lower():
                jurisdiction = "international"
            else:
                jurisdiction = "india"  # default
        
        # Split content into chunks
        chunks = self.text_splitter.split_text(content)
        
        if not chunks:
            return 0
        
        # Prepare chunk metadata
        title = metadata.get("title", os.path.basename(filepath).replace(".md", "").replace("_", " ").title())
        
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            
            # Detect section from chunk content
            section = self._detect_section(chunk)
            
            chunk_metadata = {
                "doc_id": doc_id,
                "content_hash": content_hash,
                "chunk_index": i,
                "title": title,
                "jurisdiction": jurisdiction,
                "category": metadata.get("category", "general"),
                "statute_type": metadata.get("statute_type", ""),
                "last_amended": metadata.get("last_amended", ""),
                "official_source": metadata.get("official_source", ""),
                "section": section or metadata.get("sections_covered", [""])[0] if metadata.get("sections_covered") else "",
                "source_file": os.path.basename(filepath),
            }
            
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append(chunk_metadata)
        
        # Generate embeddings
        embeddings = self.embedding_service.embed_documents(documents)
        
        # Upsert into ChromaDB
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        return len(chunks)
    
    def _detect_section(self, chunk: str) -> Optional[str]:
        """Try to detect which statutory section a chunk belongs to."""
        import re
        
        # Look for section/article/rule headings
        patterns = [
            r"##?\s*Section\s+(\d+[\w()]*)",
            r"##?\s*Article\s+(\d+[\w()]*)",
            r"##?\s*Rule\s+(\d+[\w()]*)",
            r"Section\s+(\d+[\w()]*)\s*[.:\-—]",
            r"Article\s+(\d+[\w()]*)\s*[.:\-—]",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, chunk, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def get_corpus_stats(self) -> dict:
        """Get statistics about the corpus."""
        total_chunks = self.collection.count()
        
        return {
            "total_chunks": total_chunks,
            "corpus_dir": self.corpus_dir,
            "corpus_exists": os.path.exists(self.corpus_dir),
        }


def run_ingestion(force: bool = False):
    """Standalone function to run corpus ingestion."""
    ingestor = CorpusIngestor()
    stats = ingestor.ingest_all(force=force)
    print(f"\n📊 Ingestion Results:")
    print(f"   Documents processed: {stats['processed']}")
    print(f"   Documents skipped:   {stats['skipped']}")
    print(f"   Errors:              {stats['errors']}")
    print(f"   Total chunks added:  {stats['chunks_added']}")
    return stats


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv
    run_ingestion(force=force)
