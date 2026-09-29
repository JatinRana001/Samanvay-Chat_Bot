import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class ApprovalRule(Base):
    __tablename__ = "approval_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    approval_id = Column(String(36), ForeignKey("approvals.id", ondelete="CASCADE"), nullable=False)
    industry = Column(String(255), nullable=True)
    industry_label_raw = Column(String(255), nullable=True)
    sub_sector = Column(String(255), nullable=True)
    activity = Column(String(255), nullable=True)
    state = Column(String(100), nullable=False, default="Maharashtra")
    district = Column(String(150), nullable=True)
    investment_min = Column(Numeric(15, 2), nullable=True)
    investment_max = Column(Numeric(15, 2), nullable=True)
    employee_min = Column(Integer, nullable=True)
    employee_max = Column(Integer, nullable=True)
    project_stage = Column(String(100), nullable=True)
    construction_required = Column(Boolean, nullable=True)
    hazardous_materials = Column(Boolean, nullable=True)
    pollution_category = Column(String(50), nullable=True)
    conditions = Column(JSON, default=dict)
    applicability = Column(String(100), nullable=False)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    approval = relationship("Approval", back_populates="rules")
