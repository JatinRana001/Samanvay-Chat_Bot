"""One-time in-place migration for legacy industry labels in the configured DB."""

from app.database import SessionLocal
from app.industry_taxonomy import CANONICAL_INDUSTRIES, normalize_industry, normalize_rule_industry
from app.models import ApprovalRule, Industry


def normalize_database_industries():
    db = SessionLocal()
    try:
        industries = db.query(Industry).all()
        canonical_names = {}
        for industry in industries:
            canonical, _ = normalize_industry(industry.name)
            if canonical not in CANONICAL_INDUSTRIES:
                raise ValueError(f"Unknown Industry.name {industry.name!r} (id={industry.id!r})")
            if canonical in canonical_names and canonical_names[canonical] != industry.id:
                raise ValueError(f"Multiple Industry rows resolve to canonical name {canonical!r}")
            canonical_names[canonical] = industry.id

        changed_industries = 0
        for industry in industries:
            canonical, _ = normalize_industry(industry.name)
            if industry.name != canonical:
                industry.name = canonical
                changed_industries += 1

        changed_rules = 0
        for rule in db.query(ApprovalRule).all():
            if not rule.industry:
                continue
            canonical, sub_sector = normalize_rule_industry(rule.industry, rule.sub_sector)
            if canonical not in CANONICAL_INDUSTRIES:
                raise ValueError(f"Unknown approval_rules.industry {rule.industry!r} (rule id={rule.id!r})")
            if rule.industry != canonical or rule.sub_sector != sub_sector:
                rule.industry = canonical
                rule.sub_sector = sub_sector
                changed_rules += 1

        db.commit()
        return changed_industries, changed_rules
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    industries, rules = normalize_database_industries()
    print(f"Canonicalized Industry rows: {industries}")
    print(f"Canonicalized approval rule rows: {rules}")
