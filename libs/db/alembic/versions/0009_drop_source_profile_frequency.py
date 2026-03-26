"""Drop source profile frequency granularity metadata.

Revision ID: 0009_drop_source_profile_frequency
Revises: 0008_dataset_discovery_indexes
Create Date: 2026-03-25
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0009_drop_source_profile_frequency"
down_revision: str | None = "0008_dataset_discovery_indexes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Remove deprecated source frequency label column."""

    op.drop_column("source_profiles", "frequency_granularity")


def downgrade() -> None:
    """Restore deprecated source frequency label column."""

    op.add_column(
        "source_profiles",
        sa.Column(
            "frequency_granularity",
            sa.String(length=32),
            nullable=False,
            server_default="daily",
        ),
    )
    op.alter_column("source_profiles", "frequency_granularity", server_default=None)
