"""HTTP-level coverage for the ten Samanvay evaluation scenarios."""
from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.approval import Approval
from app.models.rule import ApprovalRule

client = TestClient(app)


def recommend(**profile):
    response = client.post("/api/recommend-approvals", json=profile)
    assert response.status_code == 200, response.text
    return response.json()


def test_01_food_processing_pune_http():
    result = recommend(industry="Agro & Food Processing", district="Pune", investment_inr=25_000_000, employee_count=30, pollution_category="Orange")
    assert result["approvals"]
    assert all(a["official_source"] and "Verification date not recorded in source dataset" in result["explanation"] for a in result["approvals"])
    assert result["explanation"]


def test_02_textile_nashik_http():
    result = recommend(industry="Textiles (incl. Technical Textiles)", district="Nashik", investment_inr=15_000_000, employee_count=25, pollution_category="Orange", activity="processing/dyeing")
    assert any("Consent to Establish" in a["name"] for a in result["approvals"])


def test_03_automobile_sambhajinagar_http():
    result = recommend(industry="Automobile & Auto Components", district="Chhatrapati Sambhajinagar (Aurangabad)", investment_inr=80_000_000, employee_count=60, pollution_category="Orange")
    assert result["approvals"]


def test_04_it_mumbai_http():
    result = recommend(industry="Information Technology (IT) & IT-Enabled Services (ITeS)", district="Mumbai Suburban", investment_inr=5_000_000, employee_count=30, pollution_category="White")
    assert result["approvals"]


def test_05_pharmaceutical_thane_http():
    result = recommend(industry="Pharmaceuticals & Chemicals", district="Thane", investment_inr=200_000_000, employee_count=120, pollution_category="Red", hazardous_materials=True)
    assert result["approvals"]


def test_06_small_manufacturing_minimal_chat_http():
    response = client.post("/api/chat", json={"message": "I want to start a small workshop in Thane with 5 workers"})
    assert response.status_code == 200
    profile = response.json()["extracted_profile"]
    assert profile["industry"] is None
    assert profile["district"] == "Thane" and profile["employee_count"] == 5
    assert "industry" in response.json()["missing_fields"]


def test_07_insufficient_information_asks_without_guessing_http():
    response = client.post("/api/chat", json={"message": "I want to start a business"})
    payload = response.json()
    assert response.status_code == 200 and payload["ready_for_recommendation"] is False
    assert payload["extracted_profile"]["industry"] is None
    assert payload["extracted_profile"]["district"] is None
    assert payload["missing_fields"]
    assert payload["message"]


def test_08_unknown_approval_not_invented_http():
    response = client.post("/api/rag/query", json={"query": "space rocket launching license from MIDC", "top_k": 3, "min_similarity": 0.95})
    assert response.status_code == 200
    assert response.json()["total_found"] == 0


def test_09_non_maharashtra_is_out_of_scope_http():
    response = client.post("/api/chat", json={"message": "Set up a textile mill in Surat, Gujarat"})
    assert response.status_code == 200
    assert response.json()["out_of_scope"] is True
    assert "Gujarat" in response.json()["message"]


def test_10_old_approval_is_flagged_through_http():
    approval_id = None
    try:
        db = SessionLocal()
        approval = Approval(name="[TEST] Historical approval", department_id="dept-mpcb-001", description="staleness test", official_source="https://maharashtra.gov.in/test", last_verified=date.today() - timedelta(days=200), status="ACTIVE", is_demo=True)
        db.add(approval)
        db.commit()
        db.refresh(approval)
        approval_id = approval.id
        db.add(ApprovalRule(approval_id=approval_id, state="Maharashtra", applicability="Information required"))
        db.commit()
        db.close()
        result = recommend(industry="Agro & Food Processing", district="Pune")
        stale = next(item for item in result["approvals"] if item["approval_id"] == approval_id)
        assert stale["is_potentially_outdated"] is True
    finally:
        if approval_id:
            db = SessionLocal()
            db.query(ApprovalRule).filter(ApprovalRule.approval_id == approval_id).delete()
            db.query(Approval).filter(Approval.id == approval_id).delete()
            db.commit()
            db.close()
