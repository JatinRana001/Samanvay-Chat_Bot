"""Add source provenance, nullable verification dates, and chat sessions."""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002_grounding_and_sessions"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("approvals") as batch:
        batch.alter_column("last_verified", existing_type=sa.Date(), nullable=True)
        batch.add_column(sa.Column("source_workbook", sa.String(500), nullable=True))
        batch.add_column(sa.Column("source_row", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("imported_at", sa.DateTime(), nullable=True))
        batch.add_column(sa.Column("official_portal_raw", sa.Text(), nullable=True))
    with op.batch_alter_table("documents") as batch:
        batch.add_column(sa.Column("source_workbook", sa.String(500), nullable=True))
        batch.add_column(sa.Column("source_row", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("imported_at", sa.DateTime(), nullable=True))
    with op.batch_alter_table("approval_rules") as batch:
        batch.add_column(sa.Column("industry_label_raw", sa.String(255), nullable=True))
    with op.batch_alter_table("approval_documents") as batch:
        batch.add_column(sa.Column("source", sa.String(255), nullable=True))
        batch.add_column(sa.Column("needs_review", sa.Boolean(), nullable=True, server_default=sa.false()))
    with op.batch_alter_table("regulatory_chunks") as batch:
        batch.add_column(sa.Column("embedding_model", sa.String(255), nullable=True))
        batch.add_column(sa.Column("embedding_dim", sa.Integer(), nullable=True))
    with op.batch_alter_table("regulatory_documents") as batch:
        batch.alter_column("last_verified", existing_type=sa.Date(), nullable=True)
    op.create_table(
        "chat_sessions",
        sa.Column("session_id", sa.String(36), primary_key=True),
        sa.Column("profile_json", sa.JSON(), nullable=False),
        sa.Column("last_entities", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("chat_sessions")
    with op.batch_alter_table("regulatory_chunks") as batch:
        batch.drop_column("embedding_dim")
        batch.drop_column("embedding_model")
    with op.batch_alter_table("regulatory_documents") as batch:
        batch.alter_column("last_verified", existing_type=sa.Date(), nullable=False)
    with op.batch_alter_table("approval_documents") as batch:
        batch.drop_column("needs_review")
        batch.drop_column("source")
    with op.batch_alter_table("approval_rules") as batch:
        batch.drop_column("industry_label_raw")
    with op.batch_alter_table("documents") as batch:
        batch.drop_column("imported_at")
        batch.drop_column("source_row")
        batch.drop_column("source_workbook")
    with op.batch_alter_table("approvals") as batch:
        batch.drop_column("official_portal_raw")
        batch.drop_column("imported_at")
        batch.drop_column("source_row")
        batch.drop_column("source_workbook")
