from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import (
    ChatRequest, ChatResponse, WebsiteAssistantRequest, WebsiteAssistantResponse,
)
from app.schemas.profile import BusinessProfileUpdateRequest, BusinessProfileResponse
from app.services.session_service import SessionService
from app.services.website_faq import answer_website_question

router = APIRouter(prefix="/api", tags=["Chat & Business Profile"])

@router.post("/chat", response_model=ChatResponse)
def handle_chat_message(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    return SessionService.process_chat_message(
        session_id=request.session_id,
        user_message=request.message
    )


@router.post("/website-help", response_model=WebsiteAssistantResponse)
def handle_website_help(request: WebsiteAssistantRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    return answer_website_question(request.message)

@router.post("/business-profile", response_model=BusinessProfileResponse)
def update_or_create_business_profile(request: BusinessProfileUpdateRequest):
    session_id, _ = SessionService.get_or_create_session(request.session_id)
    updated_profile = SessionService.update_profile(session_id, request.profile)
    missing = SessionService.get_missing_critical_fields(updated_profile)
    ready = (
        updated_profile.industry is not None and
        updated_profile.district is not None and
        updated_profile.investment_inr is not None
    )
    completed = [k for k, v in updated_profile.dict().items() if v is not None and k not in ["state", "additional_attributes"]]
    return BusinessProfileResponse(
        session_id=session_id,
        profile=updated_profile,
        completed_fields=completed,
        missing_critical_fields=missing,
        is_ready_for_recommendation=ready
    )

@router.get("/business-profile/{session_id}", response_model=BusinessProfileResponse)
def get_business_profile(session_id: str):
    session_id, profile = SessionService.get_or_create_session(session_id)
    missing = SessionService.get_missing_critical_fields(profile)
    ready = (
        profile.industry is not None and
        profile.district is not None and
        profile.investment_inr is not None
    )
    completed = [k for k, v in profile.dict().items() if v is not None and k not in ["state", "additional_attributes"]]
    return BusinessProfileResponse(
        session_id=session_id,
        profile=profile,
        completed_fields=completed,
        missing_critical_fields=missing,
        is_ready_for_recommendation=ready
    )
