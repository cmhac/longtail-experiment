"""Source schedule policy and eligibility snapshot persistence.

Revision ID: 0003_sched_eligibility
Revises: 0002_ingestion_runtime_conflicts
Create Date: 2026-03-21
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0003_sched_eligibility"
down_revision: str | None = "0002_ingestion_runtime_conflicts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create schedule-policy and eligibility tables plus run/outcome counter extensions."""
    op.add_column(
        "ingestion_runs",
        sa.Column("due_source_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "ingestion_runs",
        sa.Column(
            "executed_source_count", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "ingestion_runs",
        sa.Column(
            "deferred_source_count", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "ingestion_runs",
        sa.Column(
            "not_due_source_count", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "ingestion_runs",
        sa.Column(
            "failed_source_count", sa.Integer(), nullable=False, server_default="0"
        ),
    )

    op.add_column(
        "source_run_outcomes",
        sa.Column("outcome_reason_code", sa.String(length=64), nullable=True),
    )

    op.create_table(
        "source_schedule_policies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source_key", sa.String(length=255), nullable=False),
        sa.Column("cadence_type", sa.String(length=32), nullable=False),
        sa.Column("cadence_value", sa.Integer(), nullable=True),
        sa.Column(
            "timezone", sa.String(length=64), nullable=False, server_default="UTC"
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_successful_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_eligible_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "priority_class",
            sa.String(length=32),
            nullable=False,
            server_default="normal",
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_key"),
    )

    op.create_table(
        "source_eligibility_snapshots",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("source_key", sa.String(length=255), nullable=False),
        sa.Column("eligibility_state", sa.String(length=32), nullable=False),
        sa.Column("reason_code", sa.String(length=64), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "selected_for_execution",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.ForeignKeyConstraint(["run_id"], ["ingestion_runs.run_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "source_key", name="uq_eligibility_run_source"),
    )


def downgrade() -> None:
    """Drop schedule-policy additions and revert run/outcome table extensions."""
    op.drop_table("source_eligibility_snapshots")
    op.drop_table("source_schedule_policies")

    op.drop_column("source_run_outcomes", "outcome_reason_code")

    op.drop_column("ingestion_runs", "failed_source_count")
    op.drop_column("ingestion_runs", "not_due_source_count")
    op.drop_column("ingestion_runs", "deferred_source_count")
    op.drop_column("ingestion_runs", "executed_source_count")
    op.drop_column("ingestion_runs", "due_source_count")
