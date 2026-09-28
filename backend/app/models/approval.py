import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Text, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    purpose = Column(Text, nullable=True)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    official_portal = Column(String(500), nullable=True)
    official_source = Column(Text, nullable=False)
    fee = Column(String(255), nullable=True)
    processing_time = Column(String(255), nullable=True)
    validity = Column(String(255), nullable=True)
    renewal_required = Column(Boolean, default=False)
    last_verified = Column(Date, nullable=False, default=date.today)
    status = Column(String(50), default="ACTIVE")
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    department = relationship("Department")
    rules = relationship("ApprovalRule", back_populates="approval", cascade="all, delete-orphan")
    documents = relationship("ApprovalDocument", back_populates="approval", cascade="all, delete-orphan")
