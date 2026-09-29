import math
import hashlib
import logging
from typing import List
from app.config import settings

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    types = None
    GEMINI_AVAILABLE = False

class EmbeddingService:
    DIMENSION = 768
    MODEL_TAG = settings.EMBEDDING_MODEL.removeprefix("models/")
    last_model = "fallback-hash"
    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        api_key = settings.GEMINI_API_KEY
        if api_key and GEMINI_AVAILABLE:
            try:
                client = genai.Client(api_key=api_key)
                result = client.models.embed_content(
                    model=settings.EMBEDDING_MODEL.removeprefix("models/"),
                    contents=text,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT", output_dimensionality=cls.DIMENSION),
                )
                cls.last_model = cls.MODEL_TAG
                return result.embeddings[0].values
            except Exception as exc:
                logging.warning("Gemini document embedding failed; using deterministic fallback: %s", type(exc).__name__)
        
        # Fallback deterministic pseudo-embedding (768-dim float vector)
        cls.last_model = "fallback-hash"
        return cls._fallback_embedding(text)

    @classmethod
    def get_query_embedding(cls, query: str) -> List[float]:
        api_key = settings.GEMINI_API_KEY
        if api_key and GEMINI_AVAILABLE:
            try:
                client = genai.Client(api_key=api_key)
                result = client.models.embed_content(
                    model=settings.EMBEDDING_MODEL.removeprefix("models/"),
                    contents=query,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY", output_dimensionality=cls.DIMENSION),
                )
                cls.last_model = cls.MODEL_TAG
                return result.embeddings[0].values
            except Exception as exc:
                logging.warning("Gemini query embedding failed; using deterministic fallback: %s", type(exc).__name__)
        cls.last_model = "fallback-hash"
        return cls._fallback_embedding(query, cls.DIMENSION)

    @staticmethod
    def _fallback_embedding(text: str, dim: int = 768) -> List[float]:
        # Stable deterministic word-frequency hash embedding
        vec = [0.0] * dim
        words = text.lower().split()
        for i, word in enumerate(words):
            digest = hashlib.sha256(word.encode("utf-8")).digest()
            h = int.from_bytes(digest[:8], "big") % dim
            vec[h] += 1.0 / (1.0 + math.log(i + 1))
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)
