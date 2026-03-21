"""Contract baseline tables.

Revision ID: 0001_contract_baseline
Revises:
Create Date: 2026-03-21
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0001_contract_baseline"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create initial source profile table for baseline migration scaffolding."""
    op.create_table(
        "source_profiles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_name"),
    )


def downgrade() -> None:
    """Drop baseline tables."""
    op.drop_table("source_profiles")
