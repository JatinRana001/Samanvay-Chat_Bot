import pytest
from datetime import date
from types import SimpleNamespace
from app.database import SessionLocal
from app.rag.chunker import TextChunker
from app.rag.embedder import EmbeddingService
from app.rag.retriever import RAGRetriever


def test_rag_dimension_mismatch_uses_one_fallback_space(monkeypatch):
    chunk = SimpleNamespace(
        embedding_vector=[1.0, 0.0], chunk_text="MPCB consent requirements",
        metadata_json={"embedding_model": "old-model", "embedding_dim": 2},
        document=SimpleNamespace(id="doc", title="Test", department=None, source_url="https://example.test",
                                 last_verified=date.today()),
    )
    query = SimpleNamespace(options=lambda *args, **kwargs: query, all=lambda: [chunk])
    db = SimpleNamespace(query=lambda *args, **kwargs: query)
    monkeypatch.setattr(EmbeddingService, "get_query_embedding", classmethod(lambda cls, text: [0.2, 0.8]))
    monkeypatch.setattr(EmbeddingService, "last_model", "new-model")
    results = RAGRetriever.retrieve_chunks(db, "MPCB consent", top_k=1, min_similarity=0)
    assert len(results) == 1

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
        assert results[0].source_url.startswith("workbook://")
        assert results[0].last_verified is None
    finally:
        db.close()
from datetime import date
from types import SimpleNamespace

