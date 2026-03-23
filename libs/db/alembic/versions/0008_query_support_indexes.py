"""Add query-support indexes for Phase 1 API read endpoints.

Revision ID: 0008_query_support_indexes
Revises: 0007_dataset_metadata_topic_tags
Create Date: 2026-03-23

Feature 014: Read-Only FastAPI API. This migration adds indexes to support
the five conflict filter parameters on GET /api/conflicts and the ORDER BY
used by GET /api/runs. Without these indexes every conflict query is a full
sequential scan, and the run list query cannot use an index for the sort.

Index justification:
  conflict_records.run_id           -- GET /api/conflicts?run_id=X
  conflict_records.source_key       -- GET /api/conflicts?source_key=X
  conflict_records.series_key       -- GET /api/conflicts?series_key=X
  conflict_records.reference_period_key -- GET /api/conflicts?reference_period_key=X
  conflict_records.conflict_state   -- GET /api/conflicts?conflict_state=X
  ingestion_runs.started_at         -- GET /api/runs ORDER BY started_at DESC

Note: source_run_outcomes and source_eligibility_snapshots already have
composite unique constraints on (run_id, source_key) whose B-tree index
prefix satisfies WHERE run_id = :run_id efficiently.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0008_query_support_indexes"
down_revision: str | None = "0007_dataset_metadata_topic_tags"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add query-support indexes for Phase 1 API filter and sort operations."""
    op.create_index(
        "ix_conflict_records_run_id",
        "conflict_records",
        ["run_id"],
        unique=False,
    )
    op.create_index(
        "ix_conflict_records_source_key",
        "conflict_records",
        ["source_key"],
        unique=False,
    )
    op.create_index(
        "ix_conflict_records_series_key",
        "conflict_records",
        ["series_key"],
        unique=False,
    )
    op.create_index(
        "ix_conflict_records_reference_period_key",
        "conflict_records",
        ["reference_period_key"],
        unique=False,
    )
    op.create_index(
        "ix_conflict_records_conflict_state",
        "conflict_records",
        ["conflict_state"],
        unique=False,
    )
    op.create_index(
        "ix_ingestion_runs_started_at",
        "ingestion_runs",
        ["started_at"],
        unique=False,
    )


def downgrade() -> None:
    """Remove query-support indexes."""
    op.drop_index("ix_ingestion_runs_started_at", table_name="ingestion_runs")
    op.drop_index("ix_conflict_records_conflict_state", table_name="conflict_records")
    op.drop_index(
        "ix_conflict_records_reference_period_key", table_name="conflict_records"
    )
    op.drop_index("ix_conflict_records_series_key", table_name="conflict_records")
    op.drop_index("ix_conflict_records_source_key", table_name="conflict_records")
    op.drop_index("ix_conflict_records_run_id", table_name="conflict_records")
