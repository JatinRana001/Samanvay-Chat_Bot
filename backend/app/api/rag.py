from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.rag import RegulatoryDocument
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse, RAGChunkResult, RegulationSearchRequest
from app.rag.retriever import RAGRetriever

router = APIRouter(prefix="/api", tags=["RAG & Regulations"])

@router.post("/search-regulations")
def search_regulations(request: RegulationSearchRequest, db: Session = Depends(get_db)):
    query = request.query
    # Keyword and full text lookup across ingested workbook/regulatory text.
    docs = db.query(RegulatoryDocument).filter(
        (RegulatoryDocument.title.ilike(f"%{query}%")) | 
        (RegulatoryDocument.extracted_text.ilike(f"%{query}%"))
    ).all()
    
    return {
        "query": query,
        "results": [
            {
                "id": d.id,
                "title": d.title,
                "department": d.department,
                "source_url": d.source_url,
                "last_verified": d.last_verified,
                "verification_date_label": str(d.last_verified) if d.last_verified else "Verification date not recorded in source dataset",
                "is_demo": d.is_demo
            }
            for d in docs
        ],
        "total_found": len(docs)
    }

@router.post("/rag/query", response_model=RAGQueryResponse)
def query_rag_pipeline(request: RAGQueryRequest, db: Session = Depends(get_db)):
    results = RAGRetriever.retrieve_chunks(
        db=db,
        query=request.query,
        top_k=request.top_k,
        min_similarity=request.min_similarity
    )

    explanation = None
    if not results:
        explanation = "No matching text was found in the Samanvay dataset."
    else:
        explanation = f"Found {len(results)} matching text records in the Samanvay dataset. Check each record's source and verification date."

    return RAGQueryResponse(
        query=request.query,
        results=results,
        explanation=explanation,
        total_found=len(results)
    )
