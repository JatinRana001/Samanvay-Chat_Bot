"""Re-embed all regulatory chunks with the configured embedding model."""
from app.database import SessionLocal
from app.models.rag import RegulatoryChunk
from app.rag.embedder import EmbeddingService


def main():
    db = SessionLocal()
    try:
        for chunk in db.query(RegulatoryChunk).all():
            chunk.embedding_vector = EmbeddingService.get_embedding(chunk.chunk_text)
            chunk.embedding_model = EmbeddingService.last_model
            chunk.embedding_dim = len(chunk.embedding_vector)
            chunk.metadata_json = {
                **(chunk.metadata_json or {}),
                "embedding_model": EmbeddingService.last_model,
                "embedding_dim": len(chunk.embedding_vector),
            }
        db.commit()
        print("Regulatory chunk re-embedding complete.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
