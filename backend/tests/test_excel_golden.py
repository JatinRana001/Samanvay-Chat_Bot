import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.database import Base, get_db
from app.main import app
from app.models import Approval, ApprovalRule, Document, Industry, Location
from seeds import import_maharashtra_data
from tests.oracle import expected_applicable, WORKBOOK


def test_workbook_import_and_golden_answers(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{(tmp_path / 'golden.sqlite').as_posix()}", connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    monkeypatch.setattr(import_maharashtra_data, "SessionLocal", TestingSession)
    import_maharashtra_data.import_workbook(WORKBOOK, reset=True)

    def override_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr("app.main.check_database_connection", lambda: None)
    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as client:
            db = TestingSession()
            try:
                assert (db.query(Industry).count(), db.query(Approval).count(), db.query(ApprovalRule).count(),
                        db.query(Document).count(), db.query(Location).count()) == (20, 20, 53, 23, 30)
            finally:
                db.close()
            approvals = client.get("/api/approvals").json()
            assert len(approvals) == 20
            assert all(item["last_verified"] is None for item in approvals)
            profile = {"industry": "Pharmaceuticals & Chemicals", "district": "Nagpur", "investment_inr": 50_000_000,
                       "employee_count": 40, "pollution_category": "Orange", "hazardous_materials": True,
                       "project_stage": "Pre-establishment"}
            expected = expected_applicable(profile)
            response = client.post("/api/recommend-approvals", json=profile)
            assert response.status_code == 200, response.text
            result = response.json()
            actual = {item["approval_id"] for item in result["approvals"]}
            excluded = {item["approval_id"] for item in result["not_applicable"]}
            assert actual | excluded == set(expected)

            pharma = client.post("/api/recommend-approvals", json={
                "industry": "Pharmaceuticals & Chemicals", "district": "Nagpur",
                "investment_inr": 50_000_000, "employee_count": 40, "hazardous_materials": True,
            }).json()
            pharma_ids = {item["approval_id"] for item in pharma["approvals"]}
            assert {"APR002", "APR003", "APR006", "APR014"}.issubset(pharma_ids)
            assert {"APR004", "APR013", "APR017"}.issubset(pharma_ids)
            assert {"APR015", "APR018", "APR020"}.isdisjoint(pharma_ids)
            assert any("No applicability rule in the dataset" in item for item in pharma["baseline_registrations"])

            it_result = client.post("/api/recommend-approvals", json={
                "industry": "Information Technology (IT) & IT-Enabled Services (ITeS)",
                "district": "Mumbai Suburban", "investment_inr": 50_000_000,
            }).json()
            assert "APR018" in {item["approval_id"] for item in it_result["approvals"]}
            assert "APR020" in {item["approval_id"] for item in it_result["approvals"]}
            cto_item = next(item for item in it_result["approvals"] if item["approval_id"] == "APR003")
            assert cto_item["applicability"] == "Depends on conditions"
            assert it_result["by_category"]["APR003"]["White"] == "Not applicable"
            assert next(item for item in it_result["approvals"] if item["approval_id"] == "APR018")["applicability"] == "Potentially applicable"
            assert next(item for item in it_result["approvals"] if item["approval_id"] == "APR020")["applicability"] == "Depends on conditions"

            food_result = client.post("/api/recommend-approvals", json={
                "industry": "Agro & Food Processing", "district": "Pune", "investment_inr": 25_000_000,
            }).json()
            food_applicability = {item["approval_id"]: item["applicability"] for item in food_result["approvals"]}
            assert food_applicability["APR015"] == "Likely applicable"
            assert food_applicability["APR001"] == "Potentially applicable"

            food = client.post("/api/chat", json={"message": "Food processing unit in Pune with 2.5 crore investment"}).json()
            assert "employee_count" in food["missing_fields"]

            reply = client.post("/api/chat", json={"message": "What is the fee for Udyam registration?"}).json()["message"]
            assert "Free (no government fee)" in reply
            assert "Instant to same-day" in reply
            assert "Verification date not recorded in source dataset" in reply
            followup = client.post("/api/chat", json={"message": "What is the fee for FSSAI?"}).json()
            second = client.post("/api/chat", json={"session_id": followup["session_id"], "message": "and how long does it take?"}).json()["message"]
            assert "Typically 7-60 days depending on licence category" in second
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_golden_dataset_questions_and_scope():
    with TestClient(app) as client:
        def ask(message, session_id=None):
            response = client.post("/api/chat", json={"message": message, "session_id": session_id})
            assert response.status_code == 200, response.text
            return response.json()

        udyam = ask("What is the fee for Udyam registration?")["message"]
        for fact in ("Free (no government fee)", "Instant to same-day", "Permanent", "Renewal required:** No"):
            assert fact in udyam
        drug = ask("How long does a drug manufacturing licence take and how long is it valid?")["message"]
        assert "Commonly 60-90 days (includes inspection)" in drug and "5 years" in drug
        assert "Drug Controller" in drug or "FDA" in drug
        cto = ask("What is the validity of Consent to Operate?")["message"]
        for fact in ("1 year (Red)", "2 years (Orange)", "3 years (Green)", "White category", "5 consecutive terms"):
            assert fact in cto
        factory = ask("Do I need a factory licence for 12 workers with power?")["message"]
        for fact in ("10+ workers", "20+ workers", "50+", "Likely applicable"):
            assert fact in factory

        locations = client.get("/api/locations", params={"district": "Pune"}).json()
        assert len(locations) == 7
        assert any("Chakan" in str(item) for item in locations)
        assert any("Talegaon" in str(item) for item in locations)

        aerospace = ask("What does an aerospace and defence unit need?")["message"]
        assert "Aerospace & Defence" in aerospace and "Source:" in aerospace
        assert "RUL" in aerospace or "MRO" in aerospace
        documents = ask("Which documents are needed for CTE?")["message"]
        assert "Indicative document list - verify with the authority" in documents
        gst = ask("Is GST registration required for my unit?")["message"]
        assert "No applicability rule in the dataset" in gst

        first = ask("What is the fee for FSSAI?")
        follow = ask("and how long does it take?", first["session_id"])["message"]
        assert "Typically 7-60 days depending on licence category" in follow
        assert "not covered in the Samanvay dataset" in ask("What subsidy can I get under the MSME scheme?")["message"]
        assert ask("Set up a plant in Gujarat")["out_of_scope"] is True
        textile = ask("Textile unit in Navi Mumbai")
        assert textile["extracted_profile"]["district"] == "Thane"
        steel = ask("Steel plant in Chandrapur")
        assert steel["extracted_profile"]["district"] == "Chandrapur"
        assert "no industrial-area data" in steel["message"]
