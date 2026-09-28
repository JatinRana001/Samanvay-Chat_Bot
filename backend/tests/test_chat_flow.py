import os

import pytest
from app.schemas.profile import BusinessProfile
from app.services.session_service import SessionService
from app.services.website_faq import answer_website_question
from app.database import SessionLocal
from app.main import app
from app.models.industry import Industry
from fastapi.testclient import TestClient


def test_extracts_profile_fields_and_units():
    profile = SessionService.extract_entities_from_message(
        "Food processing unit in Pune with 2.5 crore investment and 15 workers",
        BusinessProfile(),
    )
    assert profile.industry == "Agro & Food Processing"
    assert profile.district == "Pune"
    assert profile.investment_inr == 25_000_000
    assert profile.employee_count == 15


def test_missing_field_follow_up_is_targeted():
    response = SessionService.process_chat_message(None, "I want to start a textile factory")
    assert "district" in response.missing_fields
    assert "Which" in response.message and "district" in response.message
    assert response.ready_for_recommendation is False


def test_non_maharashtra_location_is_out_of_scope():
    response = SessionService.process_chat_message(None, "Set up a textile unit in Surat, Gujarat")
    assert response.out_of_scope is True
    assert "Gujarat" in response.message


@pytest.mark.parametrize(
    "question, expected",
    [
        ("How do I register my project?", "Register Project"),
        ("How do I register?", "Register Project"),
        ("What can this website do?", "Applicant pages"),
        ("What can I do here?", "Applicant pages"),
        (
            "What's the difference between an officer login and an applicant login?",
            "Officer / Government Officer Portal",
        ),
    ],
)
def test_website_faq_answers_without_extracting_a_business_profile(question, expected):
    response = SessionService.process_chat_message(None, question)

    assert response.response_type == "website_faq"
    assert expected in response.message
    assert response.extracted_profile.industry is None
    assert response.extracted_profile.district is None
    assert response.extracted_profile.investment_inr is None
    assert response.ready_for_recommendation is False


def test_approval_guidance_question_still_uses_profile_extraction():
    response = SessionService.process_chat_message(
        None,
        "I'm setting up a pharma plant in Nagpur, what approvals do I need?",
    )

    assert response.response_type == "profile"
    assert response.extracted_profile.industry == "Pharmaceuticals & Chemicals"
    assert response.extracted_profile.district == "Nagpur"


@pytest.mark.parametrize(
    "question, expected",
    [
        ("How can I register?", "Register Project"),
        ("What can I do here?", "quick-action cards"),
        (
            "What's the difference between applicant and officer login?",
            "Officer / Government Officer Portal",
        ),
        ("Where do I check my application status?", "Applications or Dashboard"),
    ],
)
def test_website_assistant_answers_navigation_questions_only(question, expected):
    response = answer_website_question(question)

    assert response["response_type"] == "website_faq"
    assert expected in response["message"]


def test_website_assistant_redirects_regulatory_questions_without_answering_them():
    response = answer_website_question("What approvals do I need and what are the fees?")

    assert response["response_type"] == "regulatory_redirect"
    assert response["message"].startswith("That's a regulatory question")


def test_website_assistant_clarifies_ambiguous_questions_and_has_scoped_fallback():
    ambiguous = answer_website_question("How do I find approvals?")
    unknown = answer_website_question("Tell me a joke")

    assert ambiguous["response_type"] == "clarification"
    assert "website" in ambiguous["message"] and "requirements" in ambiguous["message"]
    assert unknown["response_type"] == "fallback"
    assert "homepage quick-action cards" in unknown["message"]


def test_session_remembers_fields_and_does_not_reask():
    first = SessionService.process_chat_message(None, "Food processing in Pune with 2 crore investment")
    second = SessionService.process_chat_message(first.session_id, "15 workers")
    assert second.extracted_profile.industry == "Agro & Food Processing"
    assert second.extracted_profile.district == "Pune"
    assert second.extracted_profile.investment_inr == 20_000_000
    assert second.extracted_profile.employee_count == 15
    assert "industry" not in second.missing_fields
    assert "district" not in second.missing_fields


def test_chat_maps_realistic_industry_messages_to_seeded_canonical_names():
    examples = [
        ("EV battery manufacturing unit", "Electric Vehicles (EV) Manufacturing"),
        ("aircraft component manufacturing", "Aerospace & Defence Manufacturing"),
        ("software development and BPO office", "Information Technology (IT) & IT-Enabled Services (ITeS)"),
        ("semiconductor chip manufacturing plant", "Electronic System Design & Manufacturing (ESDM) & Semiconductors"),
        ("biotech diagnostic device manufacturer", "Biotechnology, Medical & Diagnostic Devices"),
        ("food processing unit", "Agro & Food Processing"),
        ("cotton textile weaving unit", "Textiles (incl. Technical Textiles)"),
        ("solar power generation project", "Green Energy / Renewable Energy & Biofuel"),
        ("cold storage warehouse", "Logistics & Warehousing"),
        ("automobile component manufacturing", "Automobile & Auto Components"),
        ("pharmaceutical API manufacturing", "Pharmaceuticals & Chemicals"),
        ("diamond jewellery manufacturing", "Gems & Jewellery"),
        ("industrial machinery factory", "Engineering & Capital Goods"),
        ("steel rolling mill", "Cement & Steel"),
        ("mineral processing plant", "Mineral & Forest-based Industries"),
        ("commercial construction development", "Real Estate & Construction"),
        ("robotics and 3D printing unit", "Industry 4.0 (AI, Robotics, IoT, 3D Printing, Nanotechnology)"),
        ("sugar factory and dairy processing", "Dairy, Sugar & Agro-Cooperative Processing"),
        ("data center facility", "Data Centres"),
        ("global capability center", "Global Capability Centres (GCC)"),
    ]
    db = SessionLocal()
    try:
        canonical_names = {name for (name,) in db.query(Industry.name).all()}
    finally:
        db.close()
    client = TestClient(app)

    for message, expected in examples:
        response = client.post("/api/chat", json={"message": message})
        assert response.status_code == 200, response.text
        actual = response.json()["extracted_profile"]["industry"]
        assert actual == expected, message
        assert actual in canonical_names, f"{actual!r} is not in the Industries table"


@pytest.mark.skipif(
    os.getenv("RUN_REAL_DATA_INTEGRATION") != "1",
    reason="Set RUN_REAL_DATA_INTEGRATION=1 to run against the imported Supabase registry",
)
def test_real_industry_chat_profiles_match_imported_approvals():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    examples = [
        (
            "I want a textile manufacturing unit",
            "in Solapur with 2 crore investment and 20 workers",
            "Textiles (incl. Technical Textiles)",
        ),
        (
            "I want a pharmaceutical manufacturing unit",
            "in Nagpur with 5 crore investment and 25 workers",
            "Pharmaceuticals & Chemicals",
        ),
        (
            "I want an IT/ITeS office",
            "in Pune with 1 crore investment and 30 workers",
            "Information Technology (IT) & IT-Enabled Services (ITeS)",
        ),
    ]

    with SessionLocal() as db:
        canonical_names = {row.name for row in db.query(Industry).all()}

    for first_message, followup, expected_industry in examples:
        first = client.post("/api/chat", json={"message": first_message})
        assert first.status_code == 200, first.text
        first_payload = first.json()
        second = client.post(
            "/api/chat",
            json={"session_id": first_payload["session_id"], "message": followup},
        )
        assert second.status_code == 200, second.text
        chat = second.json()
        profile = chat["extracted_profile"]
        assert chat["ready_for_recommendation"] is True
        assert profile["industry"] == expected_industry
        assert profile["industry"] in canonical_names

        response = client.post("/api/recommend-approvals", json=profile)
        assert response.status_code == 200, response.text
        approvals = response.json()["approvals"]
        assert any(item["applicability"] != "Not applicable" for item in approvals), expected_industry
