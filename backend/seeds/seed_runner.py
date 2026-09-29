import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal, Base
from app.models import (
    Department,
    Industry,
    Location,
    Approval,
    ApprovalRule,
    Document,
    ApprovalDocument,
    RegulatoryDocument,
    RegulatoryChunk
)
from app.industry_taxonomy import normalize_rule_industry
from seeds.demo_data import (
    DEMO_DEPARTMENTS,
    DEMO_INDUSTRIES,
    DEMO_LOCATIONS,
    DEMO_DOCUMENTS,
    DEMO_APPROVALS,
    DEMO_APPROVAL_RULES,
    DEMO_APPROVAL_DOCUMENTS
)
from seeds.demo_rag_docs import seed_rag_documents

def seed_database(reset: bool = False):
    print("=" * 65)
    print("Samanvay Database Seed Runner -- Maharashtra Industry Setup")
    print("=" * 65)

    if reset:
        print("[1/5] Dropping existing database tables...")
        Base.metadata.drop_all(bind=engine)
        print("  [OK] Tables dropped successfully.")

    print("[2/5] Creating database schema tables...")
    Base.metadata.create_all(bind=engine)
    print("  [OK] Schema initialized successfully.")

    db = SessionLocal()
    try:
        print("[3/5] Seeding verified DEMO regulatory data...")

        for dept_data in DEMO_DEPARTMENTS:
            existing = db.query(Department).filter(Department.id == dept_data["id"]).first()
            if not existing:
                dept = Department(**dept_data)
                db.add(dept)
        db.commit()
        print(f"  [OK] Departments seeded: {len(DEMO_DEPARTMENTS)}")

        for ind_data in DEMO_INDUSTRIES:
            existing = db.query(Industry).filter(Industry.id == ind_data["id"]).first()
            if existing:
                for key, value in ind_data.items():
                    setattr(existing, key, value)
            else:
                db.add(Industry(**ind_data))
        db.commit()
        print(f"  [OK] Industries seeded: {len(DEMO_INDUSTRIES)}")

        for loc_data in DEMO_LOCATIONS:
            query = db.query(Location).filter_by(**loc_data)
            if not query.first():
                db.add(Location(**loc_data))
        db.commit()
        print(f"  [OK] Locations seeded: {len(DEMO_LOCATIONS)}")

        for doc_data in DEMO_DOCUMENTS:
            existing = db.query(Document).filter(Document.id == doc_data["id"]).first()
            if not existing:
                doc = Document(**doc_data)
                db.add(doc)
        db.commit()
        print(f"  [OK] Documents seeded: {len(DEMO_DOCUMENTS)}")

        for app_data in DEMO_APPROVALS:
            existing = db.query(Approval).filter(Approval.id == app_data["id"]).first()
            if not existing:
                app_obj = Approval(**app_data)
                db.add(app_obj)
        db.commit()
        print(f"  [OK] Approvals seeded: {len(DEMO_APPROVALS)}")

        # Repair rows left behind by older demo seeds before checking for
        # existing rule definitions, avoiding duplicate legacy/canonical rows.
        for rule in db.query(ApprovalRule).filter(ApprovalRule.is_demo.is_(True)).all():
            canonical, sub_sector = normalize_rule_industry(rule.industry, rule.sub_sector)
            if canonical:
                rule.industry = canonical
                rule.sub_sector = sub_sector
        db.commit()

        for rule_data in DEMO_APPROVAL_RULES:
            if not db.query(ApprovalRule).filter_by(**rule_data, is_demo=True).first():
                db.add(ApprovalRule(**rule_data, is_demo=True))
        db.commit()
        print(f"  [OK] Approval Rules seeded: {len(DEMO_APPROVAL_RULES)}")

        for app_doc_data in DEMO_APPROVAL_DOCUMENTS:
            existing = db.query(ApprovalDocument).filter(
                ApprovalDocument.approval_id == app_doc_data["approval_id"],
                ApprovalDocument.document_id == app_doc_data["document_id"]
            ).first()
            if not existing:
                app_doc = ApprovalDocument(**app_doc_data)
                db.add(app_doc)
        db.commit()
        print(f"  [OK] Approval Document mappings seeded: {len(DEMO_APPROVAL_DOCUMENTS)}")

        print("[4/5] Seeding DEMO regulatory knowledge base...")
        seed_rag_documents()

        print("[5/5] Seed completion verification:")
        dept_count = db.query(Department).count()
        app_count = db.query(Approval).count()
        rule_count = db.query(ApprovalRule).count()
        doc_count = db.query(Document).count()
        print(f"  * Total Departments in DB: {dept_count}")
        print(f"  * Total Approvals in DB:   {app_count}")
        print(f"  * Total Rules in DB:       {rule_count}")
        print(f"  * Total Documents in DB:   {doc_count}")
        print("=" * 65)
        print("[OK] Database is ready for Phase 3 business profile & rules testing.")
        print("=" * 65)

    except Exception as e:
        db.rollback()
        print(f"[ERROR] during database seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the Samanvay regulatory database.")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables before demo seeding.")
    parser.add_argument("--real-data", action="store_true", help="Import the Maharashtra workbook (default outside --demo).")
    parser.add_argument("--demo", action="store_true", help="Seed clearly labelled DEMO data.")
    parser.add_argument("--workbook", help="Path to the Maharashtra workbook (used with --real-data).")
    args = parser.parse_args()
    if args.real_data or not args.demo:
        from seeds.import_maharashtra_data import DEFAULT_WORKBOOK, import_workbook
        workbook = args.workbook or os.getenv("MAHARASHTRA_WORKBOOK") or DEFAULT_WORKBOOK
        import_workbook(workbook, reset=args.reset)
    else:
        seed_database(reset=args.reset)
