"""Add series ownership transition metadata persistence for multi-series adapters.

Revision ID: 0006_series_ownership_transition
Revises: 0005_source_asset_schedule_cutover
Create Date: 2026-03-22
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0006_series_ownership_transition"
down_revision: str | None = "0005_source_asset_schedule_cutover"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create series-level outcome table with ownership attribution metadata."""
    op.create_table(
        "series_run_outcomes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("source_key", sa.String(length=255), nullable=False),
        sa.Column("series_item_key", sa.String(length=255), nullable=False),
        sa.Column("canonical_series_key", sa.String(length=255), nullable=False),
        sa.Column("provider_group_key", sa.String(length=255), nullable=False),
        sa.Column("ownership_mode", sa.String(length=16), nullable=False),
        sa.Column("owner_adapter_key", sa.String(length=255), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("accepted_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "quarantined_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("outcome_reason_code", sa.String(length=64), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["run_id"], ["ingestion_runs.run_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "run_id",
            "source_key",
            "series_item_key",
            name="uq_series_outcome_run_source_series",
        ),
    )


def downgrade() -> None:
    """Drop series-level ownership transition table."""
    op.drop_table("series_run_outcomes")
