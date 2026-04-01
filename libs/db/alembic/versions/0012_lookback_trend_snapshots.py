"""Add observation-level lookback trend snapshot persistence.

Revision ID: 0012_lookback_trend_snapshots
Revises: 0011_trend_lifecycle_tables
Create Date: 2026-04-01
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0012_lookback_trend_snapshots"
down_revision: str | None = "0011_trend_lifecycle_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create lookback applicability, snapshots, and canonical descriptor tables."""

    op.create_table(
        "trend_lookback_evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_series_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("observation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lookback_points", sa.Integer(), nullable=False),
        sa.Column("applicability_state", sa.String(length=16), nullable=False),
        sa.Column("reason_code", sa.String(length=64), nullable=False),
        sa.Column("reason_detail", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["data_series_id"], ["data_series.id"]),
        sa.ForeignKeyConstraint(["observation_id"], ["observations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "data_series_id",
            "observation_id",
            "lookback_points",
            name="uq_trend_lookback_evaluations_series_observation_lookback",
        ),
        sa.CheckConstraint(
            "lookback_points > 0",
            name="ck_trend_lookback_evaluations_lookback_points_positive",
        ),
        sa.CheckConstraint(
            "applicability_state IN ('applicable', 'inapplicable')",
            name="ck_trend_lookback_evaluations_applicability_state",
        ),
    )
    op.create_index(
        "ix_trend_lookback_evaluations_series_observation",
        "trend_lookback_evaluations",
        ["data_series_id", "observation_id"],
        unique=False,
    )

    op.create_table(
        "trend_lookback_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_series_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("observation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("observed_on", sa.Date(), nullable=False),
        sa.Column("lookback_points", sa.Integer(), nullable=False),
        sa.Column("outcome_state", sa.String(length=32), nullable=False),
        sa.Column("trend_label", sa.String(length=64), nullable=True),
        sa.Column("direction", sa.String(length=16), nullable=True),
        sa.Column("strength", sa.String(length=32), nullable=True),
        sa.Column("seasonality_classification", sa.String(length=32), nullable=True),
        sa.Column("analysis_version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["data_series_id"], ["data_series.id"]),
        sa.ForeignKeyConstraint(["observation_id"], ["observations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "data_series_id",
            "observation_id",
            "lookback_points",
            name="uq_trend_lookback_snapshots_series_observation_lookback",
        ),
        sa.CheckConstraint(
            "lookback_points > 0",
            name="ck_trend_lookback_snapshots_lookback_points_positive",
        ),
        sa.CheckConstraint(
            "outcome_state IN ('significant_trend', 'no_significant_trend')",
            name="ck_trend_lookback_snapshots_outcome_state",
        ),
        sa.CheckConstraint(
            "direction IS NULL OR direction IN ('up', 'down')",
            name="ck_trend_lookback_snapshots_direction",
        ),
    )
    op.create_index(
        "ix_trend_lookback_snapshots_series_observed_on",
        "trend_lookback_snapshots",
        ["data_series_id", "observed_on"],
        unique=False,
    )

    op.create_table(
        "trend_canonical_descriptors",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_series_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("observation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("observed_on", sa.Date(), nullable=False),
        sa.Column("descriptor_state", sa.String(length=16), nullable=False),
        sa.Column("canonical_trend_label", sa.String(length=64), nullable=True),
        sa.Column("canonical_direction", sa.String(length=16), nullable=True),
        sa.Column("canonical_strength", sa.String(length=32), nullable=True),
        sa.Column("selected_lookback_points", sa.Integer(), nullable=True),
        sa.Column("weighting_version", sa.String(length=64), nullable=False),
        sa.Column("weighting_trace", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["data_series_id"], ["data_series.id"]),
        sa.ForeignKeyConstraint(["observation_id"], ["observations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "data_series_id",
            "observation_id",
            name="uq_trend_canonical_descriptors_series_observation",
        ),
        sa.CheckConstraint(
            "descriptor_state IN ('available', 'unavailable')",
            name="ck_trend_canonical_descriptors_state",
        ),
        sa.CheckConstraint(
            "canonical_direction IS NULL OR canonical_direction IN ('up', 'down')",
            name="ck_trend_canonical_descriptors_direction",
        ),
        sa.CheckConstraint(
            "selected_lookback_points IS NULL OR selected_lookback_points > 0",
            name="ck_trend_canonical_descriptors_selected_lookback_positive",
        ),
    )
    op.create_index(
        "ix_trend_canonical_descriptors_series_observed_on",
        "trend_canonical_descriptors",
        ["data_series_id", "observed_on"],
        unique=False,
    )


def downgrade() -> None:
    """Drop lookback and canonical descriptor persistence tables."""

    op.drop_index(
        "ix_trend_canonical_descriptors_series_observed_on",
        table_name="trend_canonical_descriptors",
    )
    op.drop_table("trend_canonical_descriptors")
    op.drop_index(
        "ix_trend_lookback_snapshots_series_observed_on",
        table_name="trend_lookback_snapshots",
    )
    op.drop_table("trend_lookback_snapshots")
    op.drop_index(
        "ix_trend_lookback_evaluations_series_observation",
        table_name="trend_lookback_evaluations",
    )
    op.drop_table("trend_lookback_evaluations")
