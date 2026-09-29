from typing import List
from datetime import date
import logging
from sqlalchemy.orm import Session, joinedload
from app.models.rag import RegulatoryChunk
from app.schemas.rag import RAGChunkResult
from app.rag.embedder import EmbeddingService
from app.config import settings

class RAGRetriever:
    @classmethod
    def retrieve_chunks(cls, db: Session, query: str, top_k: int = 4, min_similarity: float = 0.10) -> List[RAGChunkResult]:
        chunks = db.query(RegulatoryChunk).options(joinedload(RegulatoryChunk.document)).all()
        query_vec = EmbeddingService.get_query_embedding(query)
        model_tag = EmbeddingService.last_model
        compatible = [chunk for chunk in chunks if chunk.embedding_vector and
                      (getattr(chunk, "embedding_model", None) or (chunk.metadata_json or {}).get("embedding_model")) == model_tag and
                      (getattr(chunk, "embedding_dim", None) or (chunk.metadata_json or {}).get("embedding_dim")) == len(query_vec) == len(chunk.embedding_vector)]
        fallback_mode = not compatible and bool(chunks)
        if fallback_mode:
            logging.warning("No regulatory chunks match the active embedding space; using deterministic fallback for this query")
            query_vec = EmbeddingService._fallback_embedding(query, EmbeddingService.DIMENSION)
        
        scored_results = []
        staleness_threshold = settings.REGULATORY_STALENESS_DAYS
        today = date.today()

        for chunk in chunks:
            chunk_vec = (EmbeddingService._fallback_embedding(chunk.chunk_text, EmbeddingService.DIMENSION)
                         if fallback_mode else chunk.embedding_vector)
            if not chunk_vec:
                continue
            metadata = chunk.metadata_json or {}
            if len(query_vec) != len(chunk_vec):
                continue
            chunk_model = getattr(chunk, "embedding_model", None) or metadata.get("embedding_model")
            chunk_dim = getattr(chunk, "embedding_dim", None) or metadata.get("embedding_dim")
            if not fallback_mode and (chunk_model != model_tag or chunk_dim != len(query_vec)):
                continue
            
            sim = EmbeddingService.cosine_similarity(query_vec, chunk_vec)
            if sim >= min_similarity:
                doc = chunk.document
                days_old = (today - doc.last_verified).days if doc.last_verified else None
                is_outdated = bool(days_old is not None and days_old > staleness_threshold)

                item = RAGChunkResult(
                    document_id=doc.id,
                    title=doc.title,
                    department=doc.department,
                    source_url=doc.source_url,
                    last_verified=doc.last_verified,
                    is_potentially_outdated=is_outdated,
                    chunk_text=chunk.chunk_text,
                    similarity_score=round(sim, 4)
                )
                scored_results.append((sim, item))

        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored_results[:top_k]]
