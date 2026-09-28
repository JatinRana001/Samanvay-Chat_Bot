"""Initial database schema for Samanvay

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-26 19:30:00.000000
"""
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
