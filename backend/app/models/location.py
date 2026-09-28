import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from app.database import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    state = Column(String(100), nullable=False, default="Maharashtra")
    district = Column(String(150), nullable=False, index=True)
    taluka = Column(String(150), nullable=True)
    city = Column(String(150), nullable=True)
    industrial_area = Column(String(255), nullable=True)
    zone = Column(String(100), nullable=True)
    special_conditions = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
