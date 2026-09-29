# Troubleshooting

## Database URL and passwords

Put `DATABASE_URL` in `backend/.env`. Percent-encode special characters in a PostgreSQL password; for example, `@` must be written as `%40`. The backend checks the connection with `SELECT 1` on startup and `/api/health` reports HTTP 503 when it cannot reach the database.

## Migrations and seed data

From `backend/`, run `alembic upgrade head` before `python -m seeds.seed_runner --real-data`. The canonical workbook is under `backend/data/`. Use `python -m seeds.seed_runner --demo` only for clearly labelled demonstration data. To rebuild embeddings after changing the embedding model, run `python -m seeds.reembed`.

## CORS

Set `ALLOWED_ORIGINS` in `backend/.env` to a comma-separated list of exact frontend origins, including scheme and port, such as `http://localhost:5173`. Restart FastAPI after changing it.

## Frontend API address

Local Vite development defaults to `http://127.0.0.1:8000`; leave `VITE_API_BASE_URL` unset for local use. For a deployed frontend, set it to the public FastAPI origin and rebuild the frontend. The same frontend origin must be present in `ALLOWED_ORIGINS`.
