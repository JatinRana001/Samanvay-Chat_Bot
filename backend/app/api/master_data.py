from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Department, Industry, Location, Document

router = APIRouter(prefix="/api", tags=["Master Data"])

@router.get("/industries")
def get_industries(db: Session = Depends(get_db)):
    industries = db.query(Industry).all()
    return [
        {
            "id": ind.id,
            "name": ind.name,
            "sector": ind.sector,
            "description": ind.description,
            "basic_setup_information": ind.basic_setup_information
        }
        for ind in industries
    ]

@router.get("/locations")
def get_locations(district: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(Location)
    if district:
        query = query.filter(Location.district.ilike(f"%{district}%"))
    locations = query.all()
    return [
        {
            "id": loc.id,
            "state": loc.state,
            "district": loc.district,
            "taluka": loc.taluka,
            "city": loc.city,
            "industrial_area": loc.industrial_area,
            "zone": loc.zone
        }
        for loc in locations
    ]

@router.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    departments = db.query(Department).all()
    return [
        {
            "id": dept.id,
            "name": dept.name,
            "description": dept.description,
            "website": dept.website,
            "portal": dept.portal,
            "contact_information": dept.contact_information
        }
        for dept in departments
    ]

@router.post("/documents")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    return [
        {
            "id": doc.id,
            "name": doc.name,
            "description": doc.description,
            "issuing_authority": doc.issuing_authority,
            "validity": doc.validity,
            "format": doc.format,
            "last_verified": doc.last_verified,
            "is_demo": doc.is_demo
        }
        for doc in docs
    ]
