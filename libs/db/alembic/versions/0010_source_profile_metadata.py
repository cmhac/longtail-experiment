"""Add stable source identity and human-readable source metadata.

Revision ID: 0010_source_profile_metadata
Revises: 0009_drop_source_profile_frequency
Create Date: 2026-03-30
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0010_source_profile_metadata"
down_revision: str | None = "0009_drop_source_profile_frequency"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Persist stable source identity plus title/description metadata."""

    op.add_column(
        "source_profiles",
        sa.Column("source_key", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "source_profiles",
        sa.Column("title", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "source_profiles",
        sa.Column("description", sa.String(length=2048), nullable=True),
    )

    op.execute(
        """
        UPDATE source_profiles
        SET
            source_key = LOWER(REGEXP_REPLACE(source_name, '[^a-zA-Z0-9]+', '_', 'g')),
            title = source_name,
            description = CONCAT(source_name, ' source metadata')
        """
    )

    op.alter_column("source_profiles", "source_key", nullable=False)
    op.alter_column("source_profiles", "title", nullable=False)
    op.alter_column("source_profiles", "description", nullable=False)
    op.create_unique_constraint(
        "uq_source_profiles_source_key",
        "source_profiles",
        ["source_key"],
    )


def downgrade() -> None:
    """Remove stable source identity plus title/description metadata."""

    op.drop_constraint(
        "uq_source_profiles_source_key", "source_profiles", type_="unique"
    )
    op.drop_column("source_profiles", "description")
    op.drop_column("source_profiles", "title")
    op.drop_column("source_profiles", "source_key")
