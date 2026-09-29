from typing import Optional, List, Dict, Any
from datetime import date
from pydantic import BaseModel
from app.schemas.profile import BusinessProfile

class DocumentChecklistItem(BaseModel):
    document_id: str
    name: str
    description: Optional[str] = None
    issuing_authority: Optional[str] = None
    mandatory: bool = True
    condition: Optional[str] = None
    status: str = "missing" # "have", "missing", "info_needed"

class RecommendedApproval(BaseModel):
    approval_id: str
    name: str
    description: Optional[str] = None
    purpose: Optional[str] = None
    department_name: str
    applicability: str # 'Likely applicable', 'Potentially applicable', 'Depends on conditions', 'Information required', 'Not applicable'
    why_applicable: str
    conditions_summary: Optional[str] = None
    official_portal: Optional[str] = None
    official_source: str
    fee_info: Optional[str] = None
    processing_time: Optional[str] = None
    validity: Optional[str] = None
    renewal_required: bool = False
    last_verified: Optional[date] = None
    is_potentially_outdated: bool = False
    is_demo: bool = False
    required_documents: List[DocumentChecklistItem] = []

class SetupStep(BaseModel):
    step_number: int
    title: str
    description: str
    department_involved: Optional[str] = None

class ApprovalRecommendationResult(BaseModel):
    business_profile: BusinessProfile
    basic_setup_steps: List[SetupStep]
    approvals: List[RecommendedApproval]
    explanation: Optional[str] = None
    document_checklist: Dict[str, List[str]] # "verified_have", "missing_required", "info_needed"
    next_steps: List[str]
    baseline_registrations: List[str] = []
    not_applicable: List[Dict[str, Any]] = []
    by_category: Dict[str, Any] = {}
    assumptions: List[str] = []
    data_gaps: List[str] = []
    disclaimer: str = (
        "This assistant provides preliminary guidance based on available regulatory information. "
        "Actual approval requirements may vary based on project-specific conditions. "
        "Verify requirements with the relevant government authority before submitting an application."
    )
