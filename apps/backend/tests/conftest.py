"""Shared test fixtures for API and repository tests."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libs/db/src"))

from db.models.base import Base
from db.models.ingestion_runtime import (
    ConflictRecord,
    IngestionRun,
    SeriesRunOutcome,
    SourceEligibilitySnapshot,
    SourceRunLock,
    SourceRunOutcome,
    SourceSchedulePolicy,
)

# Only create the tables relevant to the API; avoids creating the observations
# table which uses JSONB (PostgreSQL-specific, not supported by SQLite).
_RUNTIME_TABLES = [
    SourceRunLock.__table__,
    SourceSchedulePolicy.__table__,
    IngestionRun.__table__,
    SourceRunOutcome.__table__,
    SeriesRunOutcome.__table__,
    SourceEligibilitySnapshot.__table__,
    ConflictRecord.__table__,
]


@pytest.fixture()
def db_session() -> Session:  # type: ignore[return]
    """Provide an in-memory SQLite session with runtime tables created."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine, tables=_RUNTIME_TABLES)  # type: ignore[arg-type]
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = factory()
    yield session
    session.close()
    engine.dispose()


def make_run(
    *,
    run_id: str | None = None,
    started_at: datetime | None = None,
    lifecycle_state: str = "completed",
    outcome_state: str = "success",
) -> IngestionRun:
    """Build a minimal IngestionRun for tests."""
    return IngestionRun(
        run_id=run_id or f"run-{uuid4().hex[:8]}",
        trigger_type="scheduled",
        lifecycle_state=lifecycle_state,
        outcome_state=outcome_state,
        started_at=started_at or datetime.now(UTC),
        accepted_count=0,
        quarantined_count=0,
        failed_count=0,
        duplicate_no_op_count=0,
        conflict_count=0,
        due_source_count=0,
        executed_source_count=0,
        deferred_source_count=0,
        not_due_source_count=0,
        failed_source_count=0,
    )


def make_outcome(
    run_id: str,
    source_key: str = "src.test",
    state: str = "success",
) -> SourceRunOutcome:
    """Build a minimal SourceRunOutcome for tests."""
    return SourceRunOutcome(
        run_id=run_id,
        source_key=source_key,
        state=state,
        accepted_count=0,
        quarantined_count=0,
        failed_count=0,
        duplicate_no_op_count=0,
        conflict_count=0,
    )


def make_eligibility(run_id: str, source_key: str = "src.test") -> SourceEligibilitySnapshot:
    """Build a minimal SourceEligibilitySnapshot for tests."""
    return SourceEligibilitySnapshot(
        run_id=run_id,
        source_key=source_key,
        eligibility_state="due",
        reason_code="cadence_satisfied",
        evaluated_at=datetime.now(UTC),
        selected_for_execution=True,
    )


def make_conflict(run_id: str, conflict_state: str = "open") -> ConflictRecord:
    """Build a minimal ConflictRecord for tests."""
    return ConflictRecord(
        conflict_id=f"conf-{uuid4().hex[:8]}",
        run_id=run_id,
        source_key="src.test",
        series_key="series.test",
        reference_period_key="2024-01",
        existing_observation_ref="obs-old",
        incoming_record_ref="obs-new",
        conflict_type="value_drift",
        conflict_state=conflict_state,
        created_at=datetime.now(UTC),
    )
