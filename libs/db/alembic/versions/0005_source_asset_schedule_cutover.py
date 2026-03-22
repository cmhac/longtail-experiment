"""Rationalize legacy schedule-policy and eligibility schema for source-asset cadence cutover.

Revision ID: 0005_source_asset_schedule_cutover
Revises: 0004_observation_store
Create Date: 2026-03-22

Feature 011: Per-source asset cadence ownership. This migration marks legacy
schedule-policy and eligibility tables as historical-only by adding lifecycle
metadata columns. These tables retain existing data for audit but no longer
drive active scheduling decisions.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0005_source_asset_schedule_cutover"
down_revision: str | None = "0004_observation_store"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add historical lifecycle markers to legacy schedule tables."""
    op.add_column(
        "source_schedule_policies",
        sa.Column(
            "lifecycle_state",
            sa.String(length=32),
            nullable=False,
            server_default="historical_only",
        ),
    )

    op.add_column(
        "source_eligibility_snapshots",
        sa.Column(
            "lifecycle_state",
            sa.String(length=32),
            nullable=False,
            server_default="historical_only",
        ),
    )

    op.add_column(
        "ingestion_runs",
        sa.Column("trigger_origin", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    """Remove historical lifecycle markers and trigger_origin."""
    op.drop_column("ingestion_runs", "trigger_origin")
    op.drop_column("source_eligibility_snapshots", "lifecycle_state")
    op.drop_column("source_schedule_policies", "lifecycle_state")
