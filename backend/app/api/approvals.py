from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.approval import Approval
from app.schemas.profile import BusinessProfile
from app.schemas.approval import RecommendedApproval, ApprovalRecommendationResult, DocumentChecklistItem
from app.engine.rules_evaluator import DeterministicRulesEngine
from app.services.gemini_service import GeminiExplanationService
from app.rag.retriever import RAGRetriever

router = APIRouter(prefix="/api", tags=["Approvals & Recommendations"])

@router.post("/recommend-approvals", response_model=ApprovalRecommendationResult)
def recommend_approvals(profile: BusinessProfile, db: Session = Depends(get_db)):
    """
    Evaluates business profile deterministically against statutory approval rules in the database.
    """
    result = DeterministicRulesEngine.evaluate_approvals(db, profile)
    query = " ".join(filter(None, [profile.industry, profile.district, profile.pollution_category, "Maharashtra industrial approvals"]))
    try:
        sources = RAGRetriever.retrieve_chunks(db, query, top_k=5)
    except Exception:
        sources = []
    result.explanation = GeminiExplanationService.generate_explanation(result, sources=sources)
    return result

@router.get("/approvals/{approval_id}")
def get_approval_detail(approval_id: str, db: Session = Depends(get_db)):
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail=f"Approval with ID '{approval_id}' not found in verified registry.")
    
    docs = []
    for ad in approval.documents:
        docs.append({
            "document_id": ad.document.id,
            "name": ad.document.name,
            "description": ad.document.description,
            "issuing_authority": ad.document.issuing_authority,
            "mandatory": ad.mandatory,
            "condition": ad.condition
        })

    return {
        "approval_id": approval.id,
        "name": approval.name,
        "description": approval.description,
        "purpose": approval.purpose,
        "department": approval.department.name if approval.department else None,
        "official_portal": approval.official_portal,
        "official_source": approval.official_source,
        "fee": approval.fee,
        "processing_time": approval.processing_time,
        "validity": approval.validity,
        "renewal_required": approval.renewal_required,
        "last_verified": approval.last_verified,
        "is_demo": approval.is_demo,
        "required_documents": docs
    }
