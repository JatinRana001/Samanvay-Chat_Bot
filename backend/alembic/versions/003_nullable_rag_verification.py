"""Allow workbook retrieval records to omit unrecorded verification dates."""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "003_nullable_rag_verification"
down_revision: Union[str, None] = "002_grounding_and_sessions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("regulatory_documents") as batch:
        batch.alter_column("last_verified", existing_type=sa.Date(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("regulatory_documents") as batch:
        batch.alter_column("last_verified", existing_type=sa.Date(), nullable=False)
