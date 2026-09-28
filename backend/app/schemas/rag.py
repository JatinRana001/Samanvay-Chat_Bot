from typing import Optional, List
from datetime import date
from pydantic import BaseModel

class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 4
    min_similarity: float = 0.65

class RegulationSearchRequest(BaseModel):
    query: str

class RAGChunkResult(BaseModel):
    document_id: str
    title: str
    department: Optional[str] = None
    source_url: str
    last_verified: date
    is_potentially_outdated: bool
    chunk_text: str
    similarity_score: float

class RAGQueryResponse(BaseModel):
    query: str
    results: List[RAGChunkResult]
    explanation: Optional[str] = None
    total_found: int
