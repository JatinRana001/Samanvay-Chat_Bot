import pytest
from app.database import SessionLocal
from app.schemas.profile import BusinessProfile
from app.engine.rules_evaluator import DeterministicRulesEngine
from app.models.industry import Industry
from types import SimpleNamespace
from unittest.mock import patch

def test_food_processing_pune_scenario():
    db = SessionLocal()
    try:
        profile = BusinessProfile(
            industry="Agro & Food Processing",
            district="Pune",
            investment_inr=25_000_000,
            employee_count=30,
            pollution_category="Orange",
            construction_required=True
        )
        result = DeterministicRulesEngine.evaluate_approvals(db, profile)
        
        assert len(result.approvals) > 0
        approval_names = [a.name for a in result.approvals]
        
        # Must have MPCB CTE and FSSAI License
        assert any("MPCB Consent to Establish" in name for name in approval_names)
        assert any("FSSAI" in name for name in approval_names)
        assert any("Factory Plan Approval" in name for name in approval_names)
        
        # Check that verified source is present
        cte = next(a for a in result.approvals if "MPCB Consent to Establish" in a.name)
        assert "Water Act" in cte.official_source or "MPCB" in cte.official_source
        assert cte.official_portal == "https://ecmpcb.mpcb.gov.in"
        assert len(cte.required_documents) > 0
    finally:
        db.close()

def test_auto_components_sambhajinagar_scenario():
    db = SessionLocal()
    try:
        profile = BusinessProfile(
            industry="Automobile & Auto Components",
            district="Chhatrapati Sambhajinagar (Aurangabad)",
            investment_inr=150_000_000,
            employee_count=45,
            pollution_category="Orange",
            construction_required=True
        )
        result = DeterministicRulesEngine.evaluate_approvals(db, profile)
        approval_names = [a.name for a in result.approvals]
        
        assert any("MPCB Consent to Establish" in name for name in approval_names)
        assert any("Factory Plan Approval" in name for name in approval_names)
        assert any("Fire Safety" in name for name in approval_names)
    finally:
        db.close()

def test_pharma_manufacturing_scenario():
    db = SessionLocal()
    try:
        profile = BusinessProfile(
            industry="Pharmaceuticals & Chemicals",
            district="Raigad",
            investment_inr=500_000_000,
            employee_count=120,
            pollution_category="Red",
            hazardous_materials=True
        )
        result = DeterministicRulesEngine.evaluate_approvals(db, profile)
        approval_names = [a.name for a in result.approvals]
        
        # Must have FDA Drug License and Fire NOC for hazardous
        assert any("FDA Drug Manufacturing License" in name for name in approval_names)
        assert any("Fire Safety" in name for name in approval_names)
    finally:
        db.close()

def test_staleness_flagging():
    db = SessionLocal()
    try:
        profile = BusinessProfile(
            industry="Engineering & Capital Goods",
            district="Pune",
            investment_inr=5_000_000,
            employee_count=5
        )
        result = DeterministicRulesEngine.evaluate_approvals(db, profile)
        
        # Check if outdated sample record has is_potentially_outdated = True
        outdated_item = next((a for a in result.approvals if "Historical Special Capital Subsidy" in a.name), None)
        if outdated_item:
            assert outdated_item.is_potentially_outdated is True
    finally:
        db.close()


def test_pollution_category_mismatch_rejects_rule():
    rule = SimpleNamespace(
        state="Maharashtra", industry=None, district=None, investment_min=None,
        investment_max=None, employee_min=None, construction_required=None,
        hazardous_materials=None, pollution_category="Orange", conditions={},
        applicability="Likely applicable",
    )
    approval = SimpleNamespace(rules=[rule])
    matched, *_ = DeterministicRulesEngine._evaluate_single_approval(
        approval, BusinessProfile(pollution_category="Green")
    )
    assert matched is False


def test_ruleless_approval_requires_information():
    approval = SimpleNamespace(rules=[])
    matched, applicability, *_ = DeterministicRulesEngine._evaluate_single_approval(approval, BusinessProfile())
    assert matched is True
    assert applicability == "Information required"


def test_legacy_rule_alias_is_resolved_with_warning_and_subsector_confirmation():
    rule = SimpleNamespace(
        state="Maharashtra",
        industry="Textiles (incl. Technical Textiles) - processing/dyeing",
        sub_sector=None,
        activity=None,
        district=None,
        investment_min=None,
        investment_max=None,
        employee_min=None,
        construction_required=None,
        hazardous_materials=None,
        pollution_category=None,
        conditions={},
        applicability="Likely applicable",
    )
    approval = SimpleNamespace(rules=[rule])
    with patch("app.engine.rules_evaluator.logger.warning") as warning:
        matched, applicability, why, _ = DeterministicRulesEngine._evaluate_single_approval(
            approval,
            BusinessProfile(industry="Textiles (incl. Technical Textiles)"),
        )
    assert matched is True
    assert applicability == "Information required"
    assert "sub-sector" in why
    assert any("Legacy rule industry label" in call.args[0] for call in warning.call_args_list)


def test_every_seeded_canonical_industry_matches_at_least_one_approval():
    db = SessionLocal()
    try:
        industry_names = [name for (name,) in db.query(Industry.name).all()]
        assert industry_names
        for industry_name in industry_names:
            result = DeterministicRulesEngine.evaluate_approvals(
                db,
                BusinessProfile(
                    industry=industry_name,
                    district="Pune",
                    investment_inr=25_000_000,
                    employee_count=25,
                    construction_required=True,
                ),
            )
            assert result.approvals, f"No approvals matched canonical industry {industry_name!r}"
    finally:
        db.close()
