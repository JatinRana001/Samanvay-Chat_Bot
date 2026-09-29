import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "ok"


def test_health_check_reports_database_failure_as_503():
    with patch("app.main.check_database_connection", side_effect=RuntimeError("unreachable")):
        response = client.get("/api/health")
    assert response.status_code == 503
    assert response.json() == {"database": "error"}

def test_industries_endpoint():
    response = client.get("/api/industries")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 6
    names = [i["name"] for i in data]
    assert "Agro & Food Processing" in names
    assert "Automobile & Auto Components" in names

def test_locations_endpoint():
    response = client.get("/api/locations?district=Pune")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["district"] == "Pune"

def test_departments_endpoint():
    response = client.get("/api/departments")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 7

def test_recommend_approvals_endpoint():
    payload = {
        "industry": "Agro & Food Processing",
        "district": "Pune",
        "investment_inr": 25000000,
        "employee_count": 30,
        "pollution_category": "Orange",
        "construction_required": True
    }
    response = client.post("/api/recommend-approvals", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "approvals" in data
    assert len(data["approvals"]) > 0
    assert len(data["basic_setup_steps"]) == 1
    assert len(data["next_steps"]) > 0

def test_chat_single_turn_and_progressive_flow():
    # 1. Full information message
    response = client.post("/api/chat", json={
        "message": "I want to set up an automobile component manufacturing unit in Chhatrapati Sambhajinagar with 15 Crore investment and 45 workers"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["extracted_profile"]["industry"] == "Automobile & Auto Components"
    assert data["ready_for_recommendation"] is False
    assert "sub_sector" in data["missing_fields"]
    assert data["out_of_scope"] is False

    # 2. Insufficient information message (Scenario 7)
    response2 = client.post("/api/chat", json={
        "message": "I want to start a textile factory"
    })
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["extracted_profile"]["industry"] == "Textiles (incl. Technical Textiles)"
    assert data2["ready_for_recommendation"] is False
    assert "district" in data2["missing_fields"]

    # 3. Out-of-scope state message (Scenario 9)
    response3 = client.post("/api/chat", json={
        "message": "I want to start an industry in Ahmedabad, Gujarat"
    })
    assert response3.status_code == 200
    data3 = response3.json()
    assert data3["out_of_scope"] is True
    assert "Gujarat" in data3["message"]

def test_missing_approval_lookup_error_handling():
    # Scenario 8: Unknown approval ID
    response = client.get("/api/approvals/app-unknown-999")
    assert response.status_code == 404
    assert "not found in verified registry" in response.json()["detail"]
