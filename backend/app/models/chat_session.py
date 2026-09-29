from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from app.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    session_id = Column(String(36), primary_key=True)
    profile_json = Column(JSON, nullable=False)
    last_entities = Column(JSON, nullable=False, default=dict)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
