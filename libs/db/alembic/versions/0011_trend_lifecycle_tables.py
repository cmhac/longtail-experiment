"""Add trend lifecycle persistence tables.

Revision ID: 0011_trend_lifecycle_tables
Revises: 0010_source_profile_metadata
Create Date: 2026-03-31
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0011_trend_lifecycle_tables"
down_revision: str | None = "0010_source_profile_metadata"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create trend lifecycle tables with ongoing-record constraints."""

    op.create_table(
        "trend_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_series_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trend_label", sa.String(length=64), nullable=False),
        sa.Column("direction", sa.String(length=16), nullable=False),
        sa.Column("strength", sa.String(length=32), nullable=False),
        sa.Column("seasonality_classification", sa.String(length=32), nullable=False),
        sa.Column("start_period", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_period", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_ongoing", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["data_series_id"], ["data_series.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "(is_ongoing = TRUE AND end_period IS NULL) OR (is_ongoing = FALSE)",
            name="ck_trend_records_ongoing_end_period",
        ),
    )
    op.create_index(
        "ix_trend_records_series_start",
        "trend_records",
        ["data_series_id", "start_period"],
        unique=False,
    )
    op.create_index(
        "ix_trend_records_one_ongoing_per_series",
        "trend_records",
        ["data_series_id"],
        unique=True,
        postgresql_where=sa.text("is_ongoing = TRUE"),
    )

    op.create_table(
        "trend_transition_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_series_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transition_type", sa.String(length=32), nullable=False),
        sa.Column(
            "prior_trend_record_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column("new_trend_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("trigger_observation_on", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["data_series_id"], ["data_series.id"]),
        sa.ForeignKeyConstraint(["new_trend_record_id"], ["trend_records.id"]),
        sa.ForeignKeyConstraint(["prior_trend_record_id"], ["trend_records.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_trend_transition_events_series_created",
        "trend_transition_events",
        ["data_series_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Drop trend lifecycle tables."""

    op.drop_index(
        "ix_trend_transition_events_series_created",
        table_name="trend_transition_events",
    )
    op.drop_table("trend_transition_events")
    op.drop_index("ix_trend_records_one_ongoing_per_series", table_name="trend_records")
    op.drop_index("ix_trend_records_series_start", table_name="trend_records")
    op.drop_table("trend_records")
