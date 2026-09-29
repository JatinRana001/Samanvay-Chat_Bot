# Samanvay contributor guide

## Setup and commands

- Backend setup: `cd backend`, create/activate a Python virtual environment, then `python -m pip install -r requirements.txt`.
- Apply schema: `cd backend && alembic upgrade head`.
- Import canonical workbook: `cd backend && python -m seeds.seed_runner --real-data`.
- Backend tests: `cd backend && ENVIRONMENT=test python -m pytest -q` (SQLite temporary test database; mock Gemini; no network).
- Frontend: `cd frontend && npm install`; build with `cd frontend && npm run build`.

## Data and implementation rules

- `backend/data/Maharashtra_Industry_Approvals_Database.xlsx` is the source of truth for regulatory facts. Do not invent fees, timelines, validity, documents, thresholds, districts, or legal claims; state when a fact is not covered in the dataset.
- Missing verification dates stay NULL and are displayed as “Verification date not recorded in source dataset”. Never substitute today's date.
- Keep workbook imports idempotent and validate sheet counts, industry labels, JSON, and approval references.
- Preserve raw rule industry labels alongside canonical industry and sub-sector values.
- Answers must be deterministic and work with an empty `GEMINI_API_KEY`; Gemini may only paraphrase already-grounded facts and failures fall back to deterministic text.
- Do not run, edit, or delete `write_*.py` or `setup_step1.py`; they are legacy scaffolding.
- Never read, print, or commit `backend/.env` or secrets.
- Tests use SQLite and mocked Gemini. Do not require network access.
