import sys
import os
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine
from app.models.rag import RegulatoryDocument, RegulatoryChunk
from app.rag.chunker import TextChunker
from app.rag.embedder import EmbeddingService

DEMO_RAG_DOCUMENTS = [
    {
        "id": "reg-doc-psi-001",
        "title": "[DEMO] Maharashtra Industrial Policy 2019 — Package Scheme of Incentives (PSI)",
        "department": "Directorate of Industries, Maharashtra",
        "source_url": "https://industry.maharashtra.gov.in/policies/psi-2019.pdf",
        "publication_date": date(2019, 4, 1),
        "effective_date": date(2019, 4, 1),
        "last_verified": date(2024, 6, 1),
        "category": "Incentives & Subsidies",
        "state": "Maharashtra",
        "is_demo": True,
        "extracted_text": """
        MAHARASHTRA INDUSTRIAL POLICY 2019 — PACKAGE SCHEME OF INCENTIVES (PSI)
        1. Categorization of Talukas: For the purpose of grant of incentives under PSI-2019, the talukas in Maharashtra are categorized into Zone A, Zone B, Zone C, Zone D, Zone D+, and No Industry Districts.
        2. Micro, Small, and Medium Enterprises (MSME) Incentives: Eligible MSME units in Zone C, D, and D+ areas are entitled to Industrial Promotion Subsidy (IPS) equivalent to 40% to 100% of eligible gross fixed capital investment.
        3. Power Tariff Subsidy: Eligible new MSMEs in Vidarbha, Marathwada, and North Maharashtra receive electricity tariff subsidy of ₹1.00 per unit for 3 to 5 years.
        4. Stamp Duty & Electricity Duty Exemption: 100% exemption from payment of Stamp Duty for acquiring land or leasing premises in designated industrial areas and IT parks.
        5. Interest Subsidy: 5% interest subsidy on term loans for new MSMEs setting up in priority sectors including food processing, textile parks, and auto component manufacturing clusters.
        """
    },
    {
        "id": "reg-doc-mpcb-002",
        "title": "[DEMO] MPCB Guidelines for Categorization of Industrial Sectors (Red/Orange/Green/White)",
        "department": "Maharashtra Pollution Control Board (MPCB)",
        "source_url": "https://ecmpcb.mpcb.gov.in/guidelines/categorization-2020.pdf",
        "publication_date": date(2020, 1, 15),
        "effective_date": date(2020, 1, 15),
        "last_verified": date(2024, 6, 15),
        "category": "Environmental Clearances",
        "state": "Maharashtra",
        "is_demo": True,
        "extracted_text": """
        MAHARASHTRA POLLUTION CONTROL BOARD (MPCB) CLASSIFICATION CRITERIA
        1. Pollution Index (PI) Score: Industrial sectors are classified based on their composite Pollution Index score:
           - Red Category: PI score of 60 and above (Heavily polluting, e.g. API pharmaceutical manufacturing, chemical synthesis, wet textile dyeing, large distilleries). Requires stringent effluent treatment plants and prior Consent to Establish.
           - Orange Category: PI score of 41 to 59 (Moderately polluting, e.g. food processing, automobile component machining, fabrication, dairy plants). Requires Consent to Establish and Consent to Operate.
           - Green Category: PI score of 21 to 40 (Low pollution potential, e.g. small assembly, dry packaging, grain milling). Eligible for simplified single-step auto-renewal consent.
           - White Category: PI score up to 20 (Non-polluting, e.g. IT/ITES software, bio-fertilizers, electronics assembly). Exempt from environmental consent requirements; only online intimation required.
        2. Timeframe for Grant of Consent: Standard processing time for CTE is 60 days for Orange and 90 days for Red category units from the date of completed application submission.
        """
    },
    {
        "id": "reg-doc-dish-003",
        "title": "[DEMO] Maharashtra Factories Rules 1963 — Factory Building Plan & License Procedure",
        "department": "Directorate of Industrial Safety & Health (DISH)",
        "source_url": "https://dish.maharashtra.gov.in/rules/factories-plan-approval.pdf",
        "publication_date": date(2021, 3, 10),
        "effective_date": date(2021, 3, 10),
        "last_verified": date(2024, 6, 15),
        "category": "Worker Safety & Licensing",
        "state": "Maharashtra",
        "is_demo": True,
        "extracted_text": """
        DIRECTORATE OF INDUSTRIAL SAFETY & HEALTH (DISH) — FACTORY ACT COMPLIANCE
        1. Threshold Applicability: Under Section 2(m)(i) of the Factories Act, 1948, any manufacturing premise employing 10 or more workers with the aid of electric power, or 20 or more workers without power, is deemed a Factory.
        2. Plan Appraisal: No civil construction of a factory building can commence without prior plan approval (Form 1) from the Chief Inspector of Factories (DISH).
        3. Mandatory Provisions: Plans must provide adequate emergency escape stairs, minimum 500 cubic feet of air space per worker, certified ventilation, fire-resistant construction, and separate sanitary facilities.
        4. License Grant: After completion of construction and before commissioning, application for Grant of License in Form 2 must be submitted online. Licenses are issued with 1 to 10 year validity options.
        """
    }
]

def seed_rag_documents():
    print("Seeding DEMO RAG regulatory documents and chunks...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        total_chunks = 0
        for doc_data in DEMO_RAG_DOCUMENTS:
            existing = db.query(RegulatoryDocument).filter(RegulatoryDocument.id == doc_data["id"]).first()
            if not existing:
                existing = RegulatoryDocument(**doc_data)
                db.add(existing)
                db.commit()
                db.refresh(existing)

            if not existing.chunks:
                raw_chunks = TextChunker.chunk_text(existing.extracted_text, chunk_size=120, overlap=30)
                for idx, chunk_text in enumerate(raw_chunks):
                    chunk_obj = RegulatoryChunk(
                        regulatory_document_id=existing.id,
                        chunk_index=idx,
                        chunk_text=chunk_text,
                        embedding_vector=None,
                        metadata_json={"source_url": existing.source_url, "department": existing.department}
                    )
                    db.add(chunk_obj)
                db.commit()
            # Refresh vectors so fallback vectors created by older randomized hashing
            # remain searchable across processes, and configured Gemini models stay current.
            for chunk in existing.chunks:
                chunk.embedding_vector = EmbeddingService.get_embedding(chunk.chunk_text)
                total_chunks += 1
            db.commit()

        print(f"[OK] RAG Seeded: {len(DEMO_RAG_DOCUMENTS)} documents, {total_chunks} chunks.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_rag_documents()
