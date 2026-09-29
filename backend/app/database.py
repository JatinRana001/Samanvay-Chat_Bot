from pathlib import Path
from urllib.parse import quote_plus, unquote

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    if database_url.startswith("postgresql+psycopg2://"):
        try:
            scheme, remainder = database_url.split("://", 1)
            userinfo, hostinfo = remainder.rsplit("@", 1)
            if ":" in userinfo:
                username, password = userinfo.split(":", 1)
                database_url = f"{scheme}://{username}:{quote_plus(unquote(password))}@{hostinfo}"
            return make_url(database_url).render_as_string(hide_password=False)
        except Exception as exc:
            raise RuntimeError("DATABASE_URL is malformed or unreachable") from exc
    return database_url


DATABASE_URL = settings.DATABASE_URL
if not DATABASE_URL:
    if settings.ENVIRONMENT.lower() not in {"development", "test"}:
        raise RuntimeError("DATABASE_URL must be set outside development/test environments")
    DATABASE_URL = f"sqlite:///{(Path(__file__).resolve().parents[1] / 'samanvay_dev.db').as_posix()}"

DATABASE_URL = normalize_database_url(DATABASE_URL)

if DATABASE_URL.startswith("sqlite"):
    if settings.ENVIRONMENT.lower() not in {"development", "test"}:
        raise RuntimeError("SQLite is only supported in development/test environments")
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=5)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise RuntimeError("DATABASE_URL is unreachable or malformed") from exc
