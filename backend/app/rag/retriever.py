from typing import List
from datetime import date
from sqlalchemy.orm import Session, joinedload
from app.models.rag import RegulatoryChunk
from app.schemas.rag import RAGChunkResult
from app.rag.embedder import EmbeddingService
from app.config import settings

class RAGRetriever:
    @classmethod
    def retrieve_chunks(cls, db: Session, query: str, top_k: int = 4, min_similarity: float = 0.10) -> List[RAGChunkResult]:
        query_vec = EmbeddingService.get_query_embedding(query)
        chunks = db.query(RegulatoryChunk).options(joinedload(RegulatoryChunk.document)).all()
        
        scored_results = []
        staleness_threshold = settings.REGULATORY_STALENESS_DAYS
        today = date.today()

        for chunk in chunks:
            chunk_vec = chunk.embedding_vector
            if not chunk_vec:
                continue
            
            sim = EmbeddingService.cosine_similarity(query_vec, chunk_vec)
            if sim >= min_similarity:
                doc = chunk.document
                days_old = (today - doc.last_verified).days
                is_outdated = days_old > staleness_threshold

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
