import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Text, Integer, Boolean, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class RegulatoryDocument(Base):
    __tablename__ = "regulatory_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    department = Column(String(255), nullable=True)
    source_url = Column(Text, nullable=False)
    publication_date = Column(Date, nullable=True)
    effective_date = Column(Date, nullable=True)
    last_verified = Column(Date, nullable=True, default=None)
    extracted_text = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    state = Column(String(100), nullable=False, default="Maharashtra")
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("RegulatoryChunk", back_populates="document", cascade="all, delete-orphan")

class RegulatoryChunk(Base):
    __tablename__ = "regulatory_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    regulatory_document_id = Column(String(36), ForeignKey("regulatory_documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding_vector = Column(JSON, nullable=True)
    embedding_model = Column(String(255), nullable=True)
    embedding_dim = Column(Integer, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("RegulatoryDocument", back_populates="chunks")
