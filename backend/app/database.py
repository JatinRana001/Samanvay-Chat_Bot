from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

DATABASE_URL = settings.DATABASE_URL
if not DATABASE_URL:
    if settings.ENVIRONMENT.lower() not in {"development", "test"}:
        raise RuntimeError("DATABASE_URL must be set outside development/test environments")
    DATABASE_URL = "sqlite:///./samanvay_dev.db"

# SQLAlchemy 2.1 defaults the generic ``postgresql://`` URL to psycopg v3.
# This project installs psycopg2-binary, so select that driver explicitly.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

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
