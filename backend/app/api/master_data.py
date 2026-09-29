from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Department, Industry, Location, Document
from app.models import Approval
from app.services.knowledge import normalize_district

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

@router.get("/industries/{industry_id}")
def get_industry_detail(industry_id: str, db: Session = Depends(get_db)):
    industry = db.query(Industry).filter(Industry.id == industry_id).first()
    if not industry:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Industry not found in the Samanvay dataset")
    return {"id": industry.id, "name": industry.name, "sector": industry.sector,
            "description": industry.description, "basic_setup_information": industry.basic_setup_information}

@router.get("/locations")
def get_locations(district: Optional[str] = Query(None), city: Optional[str] = Query(None), taluka: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(Location)
    if district:
        normalized = normalize_district(district) or district
        query = query.filter(Location.district.ilike(f"%{normalized}%"))
    if city:
        query = query.filter(Location.city.ilike(f"%{city}%"))
    if taluka:
        query = query.filter(Location.taluka.ilike(f"%{taluka}%"))
    locations = query.all()
    return [
        {
            "id": loc.id,
            "state": loc.state,
            "district": loc.district,
            "taluka": loc.taluka,
            "city": loc.city,
            "industrial_area": loc.industrial_area,
            "zone": loc.special_conditions.get("summary") if loc.special_conditions else loc.zone,
            "special_zone": loc.special_conditions.get("summary") if loc.special_conditions else None
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

@router.get("/documents")
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
            "verification_date_label": str(doc.last_verified) if doc.last_verified else "Verification date not recorded in source dataset",
            "is_demo": doc.is_demo
        }
        for doc in docs
    ]


@router.post("/documents", deprecated=True)
def list_documents_legacy(db: Session = Depends(get_db)):
    return list_documents(db)
