from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel
from app.schemas.profile import BusinessProfile

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    message: str
    extracted_profile: BusinessProfile
    missing_fields: List[str]
    response_type: Literal["profile", "website_faq", "knowledge"] = "profile"
    quick_suggestions: List[str] = []
    ready_for_recommendation: bool = False
    out_of_scope: bool = False
    scope_notice: Optional[str] = None
    disclaimer: str = (
        "This assistant provides preliminary guidance based on available regulatory information. "
        "Actual approval requirements may vary based on project-specific conditions. "
        "Verify requirements with the relevant government authority before submitting an application."
    )


class WebsiteAssistantRequest(BaseModel):
    message: str


class WebsiteAssistantResponse(BaseModel):
    message: str
    response_type: Literal["website_faq", "regulatory_redirect", "clarification", "fallback"]
