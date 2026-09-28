import os

BASE = r"c:\Users\jatin\OneDrive\Desktop\Samanvay"

files = {
    os.path.join(BASE, "backend", "requirements.txt"): """fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.0
pydantic-settings>=2.2.0
python-dotenv>=1.0.1
sqlalchemy>=2.0.28
alembic>=1.13.1
pytest>=8.0.0
httpx>=0.27.0
python-multipart>=0.0.9
google-generativeai>=0.5.0
""",

    os.path.join(BASE, ".env.example"): """# Samanvay Environment Configuration Template
ENVIRONMENT=development
PORT=8000
HOST=0.0.0.0
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000
DATABASE_URL=sqlite:///./samanvay_dev.db
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash
EMBEDDING_MODEL=models/text-embedding-004
REGULATORY_STALENESS_DAYS=180
ADMIN_SECRET_KEY=samanvay-prototype-secret
""",

    os.path.join(BASE, "backend", "app", "database.py"): """import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            pass
    except Exception:
        DATABASE_URL = "sqlite:///./samanvay_dev.db"
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",

    os.path.join(BASE, "backend", "app", "models", "department.py"): """import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from app.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    portal = Column(String(500), nullable=True)
    contact_information = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
""",

    os.path.join(BASE, "backend", "app", "models", "industry.py"): """import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON
from app.database import Base

class Industry(Base):
    __tablename__ = "industries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    sector = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    basic_setup_information = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
""",

    os.path.join(BASE, "backend", "app", "models", "location.py"): """import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from app.database import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    state = Column(String(100), nullable=False, default="Maharashtra")
    district = Column(String(150), nullable=False, index=True)
    taluka = Column(String(150), nullable=True)
    city = Column(String(150), nullable=True)
    industrial_area = Column(String(255), nullable=True)
    zone = Column(String(100), nullable=True)
    special_conditions = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
""",

    os.path.join(BASE, "backend", "app", "models", "approval.py"): """import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Text, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    purpose = Column(Text, nullable=True)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    official_portal = Column(String(500), nullable=True)
    official_source = Column(Text, nullable=False)
    fee = Column(String(255), nullable=True)
    processing_time = Column(String(255), nullable=True)
    validity = Column(String(255), nullable=True)
    renewal_required = Column(Boolean, default=False)
    last_verified = Column(Date, nullable=False, default=date.today)
    status = Column(String(50), default="ACTIVE")
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    department = relationship("Department")
    rules = relationship("ApprovalRule", back_populates="approval", cascade="all, delete-orphan")
    documents = relationship("ApprovalDocument", back_populates="approval", cascade="all, delete-orphan")
""",

    os.path.join(BASE, "backend", "app", "models", "rule.py"): """import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class ApprovalRule(Base):
    __tablename__ = "approval_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    approval_id = Column(String(36), ForeignKey("approvals.id", ondelete="CASCADE"), nullable=False)
    industry = Column(String(255), nullable=True)
    sub_sector = Column(String(255), nullable=True)
    activity = Column(String(255), nullable=True)
    state = Column(String(100), nullable=False, default="Maharashtra")
    district = Column(String(150), nullable=True)
    investment_min = Column(Numeric(15, 2), nullable=True)
    investment_max = Column(Numeric(15, 2), nullable=True)
    employee_min = Column(Integer, nullable=True)
    employee_max = Column(Integer, nullable=True)
    project_stage = Column(String(100), nullable=True)
    construction_required = Column(Boolean, nullable=True)
    hazardous_materials = Column(Boolean, nullable=True)
    pollution_category = Column(String(50), nullable=True)
    conditions = Column(JSON, default=dict)
    applicability = Column(String(100), nullable=False)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    approval = relationship("Approval", back_populates="rules")
""",

    os.path.join(BASE, "backend", "app", "models", "document.py"): """import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Text, Boolean, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    issuing_authority = Column(String(255), nullable=True)
    validity = Column(String(255), nullable=True)
    format = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    last_verified = Column(Date, nullable=True, default=date.today)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ApprovalDocument(Base):
    __tablename__ = "approval_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    approval_id = Column(String(36), ForeignKey("approvals.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    mandatory = Column(Boolean, default=True)
    condition = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("approval_id", "document_id", name="uq_approval_document"),
    )

    approval = relationship("Approval", back_populates="documents")
    document = relationship("Document")
""",

    os.path.join(BASE, "backend", "app", "models", "rag.py"): """import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Text, Integer, Boolean, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class RegulatoryDocument(Base):
    __tablename__ = "regulatory_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    department = Column(String(255), nullable=True)
    source_url = Column(Text, nullable=False)
    publication_date = Column(Date, nullable=True)
    effective_date = Column(Date, nullable=True)
    last_verified = Column(Date, nullable=False, default=date.today)
    extracted_text = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    state = Column(String(100), nullable=False, default="Maharashtra")
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("RegulatoryChunk", back_populates="document", cascade="all, delete-orphan")

class RegulatoryChunk(Base):
    __tablename__ = "regulatory_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    regulatory_document_id = Column(String(36), ForeignKey("regulatory_documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding_vector = Column(JSON, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("RegulatoryDocument", back_populates="chunks")
""",

    os.path.join(BASE, "backend", "app", "models", "__init__.py"): """from app.models.department import Department
from app.models.industry import Industry
from app.models.location import Location
from app.models.approval import Approval
from app.models.rule import ApprovalRule
from app.models.document import Document, ApprovalDocument
from app.models.rag import RegulatoryDocument, RegulatoryChunk

__all__ = [
    "Department",
    "Industry",
    "Location",
    "Approval",
    "ApprovalRule",
    "Document",
    "ApprovalDocument",
    "RegulatoryDocument",
    "RegulatoryChunk",
]
""",

    os.path.join(BASE, "backend", "alembic.ini"): """[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = sqlite:///./samanvay_dev.db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
""",

    os.path.join(BASE, "backend", "alembic", "env.py"): """import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, DATABASE_URL
from app.models import *

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", DATABASE_URL)
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
""",

    os.path.join(BASE, "backend", "alembic", "script.py.mako"): """\"\"\"\${message}

Revision ID: \${up_revision}
Revises: \${down_revision | comma,n}
Create Date: \${create_date}
\"\"\"
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
\${imports if imports else ""}

revision: str = \${repr(up_revision)}
down_revision: Union[str, None] = \${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = \${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = \${repr(depends_on)}

def upgrade() -> None:
    \${upgrades if upgrades else "pass"}

def downgrade() -> None:
    \${downgrades if downgrades else "pass"}
""",

    os.path.join(BASE, "backend", "alembic", "versions", "001_initial_schema.py"): """\"\"\"Initial database schema for Samanvay

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-26 19:30:00.000000
\"\"\"
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("portal", sa.String(length=500), nullable=True),
        sa.Column("contact_information", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name")
    )
    op.create_table(
        "industries",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("sector", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("basic_setup_information", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name")
    )
    op.create_table(
        "locations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("district", sa.String(length=150), nullable=False),
        sa.Column("taluka", sa.String(length=150), nullable=True),
        sa.Column("city", sa.String(length=150), nullable=True),
        sa.Column("industrial_area", sa.String(length=255), nullable=True),
        sa.Column("zone", sa.String(length=100), nullable=True),
        sa.Column("special_conditions", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_table(
        "approvals",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("purpose", sa.Text(), nullable=True),
        sa.Column("department_id", sa.String(length=36), nullable=True),
        sa.Column("official_portal", sa.String(length=500), nullable=True),
        sa.Column("official_source", sa.Text(), nullable=False),
        sa.Column("fee", sa.String(length=255), nullable=True),
        sa.Column("processing_time", sa.String(length=255), nullable=True),
        sa.Column("validity", sa.String(length=255), nullable=True),
        sa.Column("renewal_required", sa.Boolean(), nullable=True),
        sa.Column("last_verified", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("is_demo", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_table(
        "approval_rules",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("approval_id", sa.String(length=36), nullable=False),
        sa.Column("industry", sa.String(length=255), nullable=True),
        sa.Column("sub_sector", sa.String(length=255), nullable=True),
        sa.Column("activity", sa.String(length=255), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("district", sa.String(length=150), nullable=True),
        sa.Column("investment_min", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("investment_max", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("employee_min", sa.Integer(), nullable=True),
        sa.Column("employee_max", sa.Integer(), nullable=True),
        sa.Column("project_stage", sa.String(length=100), nullable=True),
        sa.Column("construction_required", sa.Boolean(), nullable=True),
        sa.Column("hazardous_materials", sa.Boolean(), nullable=True),
        sa.Column("pollution_category", sa.String(length=50), nullable=True),
        sa.Column("conditions", sa.JSON(), nullable=True),
        sa.Column("applicability", sa.String(length=100), nullable=False),
        sa.Column("is_demo", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["approval_id"], ["approvals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("issuing_authority", sa.String(length=255), nullable=True),
        sa.Column("validity", sa.String(length=255), nullable=True),
        sa.Column("format", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("last_verified", sa.Date(), nullable=True),
        sa.Column("is_demo", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_table(
        "approval_documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("approval_id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("mandatory", sa.Boolean(), nullable=True),
        sa.Column("condition", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["approval_id"], ["approvals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("approval_id", "document_id", name="uq_approval_document")
    )
    op.create_table(
        "regulatory_documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("department", sa.String(length=255), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("publication_date", sa.Date(), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("last_verified", sa.Date(), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("is_demo", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_table(
        "regulatory_chunks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("regulatory_document_id", sa.String(length=36), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("embedding_vector", sa.JSON(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["regulatory_document_id"], ["regulatory_documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )

def downgrade() -> None:
    op.drop_table("regulatory_chunks")
    op.drop_table("regulatory_documents")
    op.drop_table("approval_documents")
    op.drop_table("documents")
    op.drop_table("approval_rules")
    op.drop_table("approvals")
    op.drop_table("locations")
    op.drop_table("industries")
    op.drop_table("departments")
"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    print(f"[OK] {os.path.basename(path)}: {os.path.getsize(path)} bytes")
