"""Store parsed official portal links as a structured list."""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "004_portal_urls"
down_revision: Union[str, None] = "003_nullable_rag_verification"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    with op.batch_alter_table("approvals") as batch:
        batch.add_column(sa.Column("official_portal_urls", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("approvals") as batch:
        batch.drop_column("official_portal_urls")
