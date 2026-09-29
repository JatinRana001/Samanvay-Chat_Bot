from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError
import logging
from sqlalchemy.orm import Session
from app.database import get_db, check_database_connection
from app.models.approval import Approval
from app.schemas.profile import BusinessProfile
from app.schemas.approval import RecommendedApproval, ApprovalRecommendationResult, DocumentChecklistItem
from app.engine.rules_evaluator import DeterministicRulesEngine
from app.services.gemini_service import GeminiExplanationService
from app.services.session_service import SessionService
from app.rag.retriever import RAGRetriever

router = APIRouter(prefix="/api", tags=["Approvals & Recommendations"])
logger = logging.getLogger(__name__)

@router.post("/recommend-approvals", response_model=ApprovalRecommendationResult)
def recommend_approvals(profile: BusinessProfile, db: Session = Depends(get_db)):
    """
    Evaluates business profile deterministically against statutory approval rules in the database.
    """
    try:
        check_database_connection()
        result = DeterministicRulesEngine.evaluate_approvals(db, profile)
    except (SQLAlchemyError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail="Approval database is unreachable") from exc
    query = " ".join(filter(None, [profile.industry, profile.district, profile.pollution_category, "Maharashtra industrial approvals"]))
    try:
        sources = RAGRetriever.retrieve_chunks(db, query, top_k=5)
    except SQLAlchemyError as exc:
        logger.warning("RAG retrieval failed during recommendation: %s", type(exc).__name__)
        sources = []
    result.explanation = GeminiExplanationService.generate_explanation(result, sources=sources)
    return result


@router.get("/recommend-approvals/by-session/{session_id}", response_model=ApprovalRecommendationResult)
def recommend_approvals_by_session(session_id: str, db: Session = Depends(get_db)):
    _, profile = SessionService.get_or_create_session(session_id)
    return recommend_approvals(profile, db)

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
        "official_portal": approval.official_portal_urls or [],
        "official_portal_raw": approval.official_portal_raw,
        "official_source": approval.official_source,
        "fee": approval.fee,
        "processing_time": approval.processing_time,
        "validity": approval.validity,
        "renewal_required": approval.renewal_required,
        "last_verified": approval.last_verified,
        "verification_date_label": str(approval.last_verified) if approval.last_verified else "Verification date not recorded in source dataset",
        "is_demo": approval.is_demo,
        "required_documents": docs
    }


@router.get("/approvals")
def list_approvals(db: Session = Depends(get_db)):
    return [{"approval_id": item.id, "name": item.name, "department": item.department.name if item.department else None,
             "fee": item.fee, "processing_time": item.processing_time, "validity": item.validity,
             "renewal_required": item.renewal_required, "official_portal": item.official_portal_urls or [],
             "official_portal_raw": item.official_portal_raw, "official_source": item.official_source,
             "last_verified": item.last_verified,
             "verification_date_label": str(item.last_verified) if item.last_verified else "Verification date not recorded in source dataset"}
            for item in db.query(Approval).filter(Approval.is_demo.is_(False)).order_by(Approval.id).all()]
