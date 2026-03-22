"""Canonical observation store tables.

Revision ID: 0004_observation_store
Revises: 0003_sched_eligibility
Create Date: 2026-03-22
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0004_observation_store"
down_revision: str | None = "0003_sched_eligibility"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create canonical observation storage tables."""
    op.add_column(
        "source_profiles",
        sa.Column("frequency_granularity", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "source_profiles",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.execute(
        """
        UPDATE source_profiles
        SET
            frequency_granularity = COALESCE(frequency_granularity, 'daily'),
            created_at = COALESCE(created_at, NOW())
        """
    )

    op.alter_column("source_profiles", "frequency_granularity", nullable=False)
    op.alter_column("source_profiles", "created_at", nullable=False)

    op.create_table(
        "data_series",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source_profile_id", sa.UUID(), nullable=False),
        sa.Column("series_key", sa.String(length=255), nullable=False),
        sa.Column("metric_name", sa.String(length=255), nullable=False),
        sa.Column("default_scale", sa.Numeric(10, 4), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_profile_id"], ["source_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("series_key"),
    )

    op.create_table(
        "observations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("series_id", sa.UUID(), nullable=False),
        sa.Column("observed_on", sa.Date(), nullable=False),
        sa.Column("value", sa.Numeric(20, 8), nullable=False),
        sa.Column("reported_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attributes", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["series_id"], ["data_series.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "series_id", "observed_on", name="uq_observation_series_date"
        ),
    )


def downgrade() -> None:
    """Drop canonical observation storage tables."""
    op.drop_table("observations")
    op.drop_table("data_series")
    op.drop_column("source_profiles", "created_at")
    op.drop_column("source_profiles", "frequency_granularity")
