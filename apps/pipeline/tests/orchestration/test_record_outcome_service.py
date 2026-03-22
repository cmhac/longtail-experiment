"""Coverage-focused tests for record outcome service branches."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.conflict_persistence_service import ConflictPersistenceService
from src.orchestration.jobs.record_outcome_service import RecordOutcomeService


class _ConflictRepository:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def add_conflict(self, payload: dict[str, object]) -> None:
        """Persist one conflict payload for assertions."""
        self.rows.append(payload)


class _RunContextRepository:
    def __init__(self) -> None:
        self.rows: list[tuple[str, dict[str, object]]] = []

    def add_run_context(self, *, run_id: str, context: dict[str, object]) -> None:
        """Persist one run-context payload for assertions."""
        self.rows.append((run_id, context))


def test_record_outcome_service_handles_accepted_and_duplicate_noop() -> None:
    """Service should return accepted/no-op without creating conflict rows."""
    conflict_repo = _ConflictRepository()
    service = RecordOutcomeService(
        conflict_persistence_service=ConflictPersistenceService(conflict_repo),
    )

    accepted = service.resolve_record_outcome(
        run_id="run-1",
        source_key="bls",
        reference_period_key="2026-01",
        incoming={"series_key": "CPI.US.ALL", "value": "301.0"},
        existing=None,
    )
    noop = service.resolve_record_outcome(
        run_id="run-1",
        source_key="bls",
        reference_period_key="2026-01",
        incoming={"series_key": "CPI.US.ALL", "value": "301.0", "attributes": {"unit": "index"}},
        existing={"value": "301.0", "attributes": {"unit": "index"}},
    )

    assert accepted["status"] == "accepted"
    assert noop["status"] == "duplicate_no_op"
    assert conflict_repo.rows == []


def test_record_outcome_service_persists_conflicts_and_run_context() -> None:
    """Service should persist conflict rows and optional run-context metadata."""
    conflict_repo = _ConflictRepository()
    run_context_repo = _RunContextRepository()
    service = RecordOutcomeService(
        conflict_persistence_service=ConflictPersistenceService(conflict_repo),
        run_context_repository=run_context_repo,
    )

    outcome = service.resolve_record_outcome(
        run_id="run-2",
        source_key="bls",
        reference_period_key="2026-02",
        incoming={
            "series_key": "CPI.US.ALL",
            "value": "303.0",
            "record_ref": "incoming-1",
        },
        existing={"value": "302.0", "observation_ref": "obs-1"},
    )
    service.persist_run_context("run-2", {"trigger_type": "on_demand"})

    assert outcome["status"] == "conflict"
    assert str(outcome["conflict_id"]).startswith("conf-")
    assert len(conflict_repo.rows) == 1
    assert run_context_repo.rows == [("run-2", {"trigger_type": "on_demand"})]
