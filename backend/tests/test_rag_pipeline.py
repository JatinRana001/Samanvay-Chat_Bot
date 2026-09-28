import pytest
from app.database import SessionLocal
from app.rag.chunker import TextChunker
from app.rag.embedder import EmbeddingService
from app.rag.retriever import RAGRetriever

def test_text_chunking():
    sample_text = "This is a test paragraph for industrial regulations. " * 30
    chunks = TextChunker.chunk_text(sample_text, chunk_size=20, overlap=5)
    assert len(chunks) > 1
    assert all(len(c.split()) <= 20 for c in chunks)

def test_embedding_cosine_similarity():
    v1 = EmbeddingService.get_embedding("Maharashtra pollution control board MPCB consent to establish")
    v2 = EmbeddingService.get_embedding("MPCB CTE environmental pollution discharge norms")
    v3 = EmbeddingService.get_embedding("Completely unrelated random topic about cooking recipes food")

    sim_related = EmbeddingService.cosine_similarity(v1, v2)
    sim_unrelated = EmbeddingService.cosine_similarity(v1, v3)
    assert sim_related > sim_unrelated

def test_rag_retriever_query():
    db = SessionLocal()
    try:
        results = RAGRetriever.retrieve_chunks(
            db=db,
            query="MPCB pollution categorization Red Orange Green White score",
            top_k=2,
            min_similarity=0.10
        )
        assert len(results) > 0
        assert any("Pollution Index" in r.chunk_text or "MPCB" in r.chunk_text for r in results)
        assert results[0].source_url.startswith("https://")
        assert results[0].last_verified is not None
    finally:
        db.close()
