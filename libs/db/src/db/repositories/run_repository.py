"""Runtime run persistence adapter for orchestration outcomes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StoredRunOutcome:
    """Stored aggregate run-level outcome snapshot."""

    run_id: str
    trigger_type: str
    outcome_state: str
    accepted_count: int
    quarantined_count: int
    failed_count: int
    duplicate_no_op_count: int
    conflict_count: int


class InMemoryRunRepository:
    """In-memory adapter used by orchestration tests and local flows."""

    def __init__(self) -> None:
        self._runs: dict[str, StoredRunOutcome] = {}

    def add_run_outcome(self, payload: StoredRunOutcome) -> None:
        """Persist one run summary by run identifier."""
        self._runs[payload.run_id] = payload

    def get_run_outcome(self, run_id: str) -> StoredRunOutcome | None:
        """Fetch one run summary if available."""
        return self._runs.get(run_id)
