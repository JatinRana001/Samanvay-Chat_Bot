from openpyxl import load_workbook
from types import SimpleNamespace

from app.schemas.profile import BusinessProfile
from app.services.session_service import SessionService
from app.engine.rules_evaluator import DeterministicRulesEngine


def test_longest_district_keys_and_workbook_districts():
    assert SessionService.extract_entities_from_message("Navi Mumbai", BusinessProfile()).district == "Thane"
    assert SessionService.extract_entities_from_message("Mumbai City", BusinessProfile()).district == "Mumbai City"
    workbook_path = __import__("pathlib").Path(__file__).parents[1] / "data" / "Maharashtra_Industry_Approvals_Database.xlsx"
    workbook = load_workbook(workbook_path, read_only=True, data_only=True)
    rows = list(workbook["Locations"].values)
    headers = [str(value).strip() if value else "" for value in rows[0]]
    district_index = next(index for index, name in enumerate(headers) if name.casefold() == "district")
    districts = {str(row[district_index]).strip() for row in rows[1:] if row[district_index]}
    for district in districts:
        resolved = SessionService.extract_entities_from_message(f"Unit in {district}", BusinessProfile()).district
        assert resolved == district
    workbook.close()


def test_profile_values_can_be_updated_and_employee_phrases_parse():
    profile = BusinessProfile(industry="Agro & Food Processing", district="Pune", investment_inr=25_000_000)
    updated = SessionService.extract_entities_from_message(
        "change investment to 5 crore; locate it in Nashik; over 50 workers", profile
    )
    assert updated.investment_inr == 50_000_000
    assert updated.district == "Nashik"
    assert updated.employee_count == 50
    assert SessionService.extract_entities_from_message("workforce of 50", profile).employee_count == 50
    assert SessionService.extract_entities_from_message("100+ workers", profile).employee_count == 100
    assert SessionService.extract_entities_from_message("50-60 employees", profile).employee_count == 50


def test_bare_worker_answer_after_worker_question():
    session_id, profile = SessionService.get_or_create_session()
    profile.industry = "Agro & Food Processing"
    profile.district = "Pune"
    profile.investment_inr = 25_000_000
    SessionService.update_profile(session_id, profile)
    SessionService.process_chat_message(session_id, "How many workers?")
    response = SessionService.process_chat_message(session_id, "35")
    assert response.extracted_profile.employee_count == 35


def test_missing_session_id_starts_new_session_with_expiry_notice():
    response = SessionService.process_chat_message("expired-session", "hello")
    assert response.session_id != "expired-session"
    assert "session expired" in response.message.casefold()


def test_rule_employee_ceiling_and_stage_set_matching():
    base = dict(id="r1", state="Maharashtra", industry=None, sub_sector=None, activity=None,
                district=None, investment_min=None, investment_max=None, employee_min=None,
                employee_max=40, project_stage="Pre-establishment / pre-operation",
                construction_required=None, hazardous_materials=None, pollution_category=None,
                conditions={}, applicability="Likely applicable")
    approval = SimpleNamespace(rules=[SimpleNamespace(**base)])
    accepted, *_ = DeterministicRulesEngine._evaluate_single_approval(
        approval, BusinessProfile(employee_count=35, project_stage="Pre-establishment")
    )
    rejected, *_ = DeterministicRulesEngine._evaluate_single_approval(
        approval, BusinessProfile(employee_count=45, project_stage="Pre-establishment")
    )
    wrong_stage, *_ = DeterministicRulesEngine._evaluate_single_approval(
        approval, BusinessProfile(employee_count=35, project_stage="Operations")
    )
    assert accepted and not rejected and not wrong_stage


def test_rule_choice_is_independent_of_row_order_and_excludes_not_applicable():
    common = dict(state="Maharashtra", industry=None, district=None, investment_min=None,
                  investment_max=None, employee_min=None, employee_max=None, project_stage=None,
                  construction_required=None, hazardous_materials=None, pollution_category=None,
                  conditions={})
    likely = SimpleNamespace(id="b", applicability="Likely applicable", **common)
    info = SimpleNamespace(id="a", applicability="Information required", **common)
    profile = BusinessProfile()
    first = DeterministicRulesEngine._evaluate_single_approval(SimpleNamespace(rules=[info, likely]), profile)
    second = DeterministicRulesEngine._evaluate_single_approval(SimpleNamespace(rules=[likely, info]), profile)
    assert first[0:2] == second[0:2] == (True, "Information required")
    not_applicable = SimpleNamespace(id="c", applicability="Not applicable", **common)
    excluded = DeterministicRulesEngine._evaluate_single_approval(SimpleNamespace(rules=[not_applicable]), profile)
    assert excluded[0] is False
