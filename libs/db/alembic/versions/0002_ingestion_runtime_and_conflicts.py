"""Runtime ingestion and conflict tables.

Revision ID: 0002_ingestion_runtime_conflicts
Revises: 0001_contract_baseline
Create Date: 2026-03-21
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0002_ingestion_runtime_conflicts"
down_revision: str | None = "0001_contract_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create runtime run-state and conflict persistence tables."""
    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("trigger_type", sa.String(length=32), nullable=False),
        sa.Column("lifecycle_state", sa.String(length=32), nullable=False),
        sa.Column("outcome_state", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accepted_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "quarantined_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "duplicate_no_op_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("conflict_count", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id"),
    )

    op.create_table(
        "source_run_locks",
        sa.Column("source_key", sa.String(length=255), nullable=False),
        sa.Column("active_run_id", sa.String(length=64), nullable=True),
        sa.Column("queued_trigger_token", sa.String(length=64), nullable=True),
        sa.Column("lock_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("source_key"),
    )

    op.create_table(
        "source_run_outcomes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("source_key", sa.String(length=255), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("accepted_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "quarantined_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "duplicate_no_op_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("conflict_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["run_id"], ["ingestion_runs.run_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "source_key", name="uq_outcome_run_source"),
    )

    op.create_table(
        "conflict_records",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("conflict_id", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("source_key", sa.String(length=255), nullable=False),
        sa.Column("series_key", sa.String(length=255), nullable=False),
        sa.Column("reference_period_key", sa.String(length=64), nullable=False),
        sa.Column("existing_observation_ref", sa.String(length=255), nullable=False),
        sa.Column("incoming_record_ref", sa.String(length=255), nullable=False),
        sa.Column("conflict_type", sa.String(length=64), nullable=False),
        sa.Column("conflict_state", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["run_id"], ["ingestion_runs.run_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("conflict_id"),
    )


def downgrade() -> None:
    """Drop runtime ingestion and conflict tables."""
    op.drop_table("conflict_records")
    op.drop_table("source_run_outcomes")
    op.drop_table("source_run_locks")
    op.drop_table("ingestion_runs")
