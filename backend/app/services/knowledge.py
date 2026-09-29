"""Deterministic read helpers for the workbook-backed knowledge registry."""
from difflib import SequenceMatcher
import re

from sqlalchemy.orm import Session, joinedload

from app.models import Approval, ApprovalDocument, ApprovalRule, Document, Industry, Location
from app.industry_taxonomy import normalize_industry, normalize_rule_industry

ALIASES = {
    "cte": "Consent to Establish (CTE)", "consent to establish": "Consent to Establish (CTE)",
    "cto": "Consent to Operate (CTO)", "consent to operate": "Consent to Operate (CTO)",
    "ec": "Environmental Clearance (EC)", "environment clearance": "Environmental Clearance (EC)",
    "factory licence": "Factory Licence (Form 2)", "factory license": "Factory Licence (Form 2)",
    "factory licence form 2": "Factory Licence (Form 2)", "factory plan approval": "Factory Plan Approval (Form 1)",
    "plan approval form 1": "Factory Plan Approval (Form 1)", "fire noc": "Fire NOC / Fire Safety Certificate",
    "building plan": "Building Plan Approval / Commencement Certificate", "commencement certificate": "Building Plan Approval / Commencement Certificate",
    "midc plot": "MIDC Industrial Plot/Land Allotment", "land allotment": "MIDC Industrial Plot/Land Allotment",
    "power load": "Power Load Sanction / Electrical Inspectorate Approval", "electrical inspectorate": "Power Load Sanction / Electrical Inspectorate Approval",
    "labour registration": "Labour Registrations (Shops & Establishment / Contract Labour Licence)", "contract labour": "Labour Registrations (Shops & Establishment / Contract Labour Licence)",
    "shops establishment": "Labour Registrations (Shops & Establishment / Contract Labour Licence)", "gumasta": "Labour Registrations (Shops & Establishment / Contract Labour Licence)",
    "explosives": "Explosives / Petroleum & Hazardous Substances Licence", "peso": "Explosives / Petroleum & Hazardous Substances Licence", "petroleum": "Explosives / Petroleum & Hazardous Substances Licence",
    "legal metrology": "Legal Metrology Registration (Weights & Measures)", "weights and measures": "Legal Metrology Registration (Weights & Measures)",
    "boiler": "Boiler Registration", "industrial licence": "Industrial Licence (IL) under IDR Act", "idr": "Industrial Licence (IL) under IDR Act",
    "udyam": "Udyam Registration (MSME)", "msme": "Udyam Registration (MSME)", "gst": "GST Registration",
    "drug licence": "Drug Manufacturing Licence", "drug license": "Drug Manufacturing Licence",
    "fssai": "FSSAI Licence/Registration", "sez": "SEZ Unit Approval",
    "stpi": "STPI Registration", "mpcb": "MPCB Consent",
}

DISTRICT_ALIASES = {
    "ahilyanagar": "Ahmednagar", "ahmednagar": "Ahmednagar",
    "aurangabad": "Chhatrapati Sambhajinagar (Aurangabad)",
    "sambhajinagar": "Chhatrapati Sambhajinagar (Aurangabad)",
    "chhatrapati sambhajinagar": "Chhatrapati Sambhajinagar (Aurangabad)",
    "osmanabad": "Dharashiv (Osmanabad)", "dharashiv": "Dharashiv (Osmanabad)",
    "navi mumbai": "Thane", "mumbai": "Mumbai Suburban",
}
DISTRICTS = ["Ahilyanagar", "Akola", "Amravati", "Beed", "Bhandara", "Buldhana", "Chandrapur", "Chhatrapati Sambhajinagar", "Dharashiv", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur", "Latur", "Mumbai City", "Mumbai Suburban", "Nagpur", "Nanded", "Nandurbar", "Nashik", "Palghar", "Parbhani", "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"]


def normalize_district(value):
    folded = (value or "").strip().casefold()
    for alias in sorted(DISTRICT_ALIASES, key=len, reverse=True):
        if folded == alias or re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", folded):
            return DISTRICT_ALIASES[alias]
    return next((district for district in sorted(DISTRICTS, key=len, reverse=True) if district.casefold() == folded), None)


def _resolve(query, names):
    q = (query or "").strip().casefold()
    if not q:
        return None
    embedded = next((name for name in sorted(names, key=len, reverse=True) if name.casefold() in q), None)
    if embedded:
        return embedded
    for alias, canonical in ALIASES.items():
        if re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", q):
            target = next((name for name in names if name.casefold() == canonical.casefold()), None)
            if target:
                return target
            target = next((name for name in names if SequenceMatcher(None, canonical.casefold(), name.casefold()).ratio() >= 0.6), None)
            if target:
                return target
    exact = next((name for name in names if name.casefold() == q), None)
    if exact:
        return exact
    query_tokens = {token for token in re.findall(r"[a-z0-9]+", q) if token not in {"what", "is", "the", "fee", "for", "how", "long", "does", "it", "take", "and", "validity", "of"}}
    scored = []
    for name in names:
        tokens = set(re.findall(r"[a-z0-9]+", name.casefold()))
        overlap = len(query_tokens & tokens) / max(1, min(len(query_tokens), len(tokens)))
        ratio = SequenceMatcher(None, " ".join(sorted(query_tokens)), " ".join(sorted(tokens))).ratio()
        scored.append((max(overlap, ratio if len(query_tokens) <= 3 else 0), name))
    scored.sort(reverse=True)
    if scored and scored[0][0] >= 0.65 and (len(scored) == 1 or scored[0][0] - scored[1][0] >= 0.08):
        return scored[0][1]
    return None


class Knowledge:
    @staticmethod
    def list_approvals(db: Session):
        return db.query(Approval).filter(Approval.is_demo.is_(False)).order_by(Approval.id).all()

    @classmethod
    def get_approval(cls, db: Session, name_or_alias):
        items = cls.list_approvals(db)
        name = _resolve(name_or_alias, [x.name for x in items])
        return next((x for x in items if x.name == name), None)

    @staticmethod
    def get_industry(db: Session, name_or_alias):
        names = [x.name for x in db.query(Industry).all()]
        name, _ = normalize_industry(name_or_alias or "")
        canonical = name if name in names else _resolve(name_or_alias, names)
        if not canonical:
            tokens = set((name_or_alias or "").casefold().replace("&", " ").split())
            candidates = sorted(((len(tokens & set(item.casefold().replace("&", " ").split())) / max(len(set(item.casefold().split())), 1), item) for item in names), reverse=True)
            if candidates and candidates[0][0] >= 0.25:
                canonical = candidates[0][1]
        return db.query(Industry).filter(Industry.name == canonical).first() if canonical else None

    @staticmethod
    def get_locations(db: Session, district=None, city=None, taluka=None, industrial_area=None):
        query = db.query(Location)
        for column, value in ((Location.district, district), (Location.city, city), (Location.taluka, taluka), (Location.industrial_area, industrial_area)):
            if value:
                query = query.filter(column.ilike(f"%{value}%"))
        return query.order_by(Location.district, Location.taluka, Location.industrial_area).all()

    @staticmethod
    def get_documents(db: Session, approval=None, document=None):
        query = db.query(Document)
        if approval:
            query = query.join(ApprovalDocument).join(Approval).filter(Approval.id == approval.id)
        if document:
            query = query.filter(Document.name.ilike(f"%{document}%"))
        return query.order_by(Document.id).all()

    @staticmethod
    def explain_rules_for(db: Session, approval):
        return db.query(ApprovalRule).filter(ApprovalRule.approval_id == approval.id).order_by(ApprovalRule.id).all()

    @staticmethod
    def explain_rules_for_industry(db: Session, industry_name):
        rules = [rule for rule in db.query(ApprovalRule).order_by(ApprovalRule.id).all()
                 if normalize_rule_industry(rule.industry, rule.sub_sector)[0] == industry_name]
        names = {item.id: item.name for item in db.query(Approval.id, Approval.name).all()}
        for rule in rules:
            rule.approval_name = names.get(rule.approval_id, rule.approval_id)
        return rules

    @classmethod
    def check_applicability(cls, db: Session, approval, profile):
        from app.engine.rules_evaluator import DeterministicRulesEngine
        return DeterministicRulesEngine._evaluate_single_approval(approval, profile)
