from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class BusinessProfile(BaseModel):
    industry: Optional[str] = Field(None, description="Industry sector")
    sub_sector: Optional[str] = None
    activity: Optional[str] = None
    state: str = Field("Maharashtra", description="State (strictly Maharashtra)")
    district: Optional[str] = Field(None, description="District in Maharashtra")
    taluka: Optional[str] = None
    industrial_area: Optional[str] = None
    investment_inr: Optional[float] = Field(None, description="Capital investment in INR")
    investment_display: Optional[str] = Field(None, description="Formatted investment display")
    employee_count: Optional[int] = Field(None, description="Estimated number of workers")
    project_stage: Optional[str] = Field(None, description="Current stage")
    construction_required: Optional[bool] = Field(None, description="Whether new building construction is needed")
    hazardous_materials: Optional[bool] = Field(None, description="Whether hazardous/flammable materials are handled")
    pollution_category: Optional[str] = Field(None, description="Red, Orange, Green, White")
    pollution_category_inferred: Optional[str] = Field(None, description="Unconfirmed sector-based category hint")
    additional_attributes: Dict[str, Any] = Field(default_factory=dict)

class BusinessProfileUpdateRequest(BaseModel):
    session_id: str
    profile: BusinessProfile

class BusinessProfileResponse(BaseModel):
    session_id: str
    profile: BusinessProfile
    completed_fields: List[str]
    missing_critical_fields: List[str]
    is_ready_for_recommendation: bool
