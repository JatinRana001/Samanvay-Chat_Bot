import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Text, Boolean, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    issuing_authority = Column(String(255), nullable=True)
    validity = Column(String(255), nullable=True)
    format = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    last_verified = Column(Date, nullable=True, default=date.today)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ApprovalDocument(Base):
    __tablename__ = "approval_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    approval_id = Column(String(36), ForeignKey("approvals.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    mandatory = Column(Boolean, default=True)
    condition = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("approval_id", "document_id", name="uq_approval_document"),
    )

    approval = relationship("Approval", back_populates="documents")
    document = relationship("Document")
