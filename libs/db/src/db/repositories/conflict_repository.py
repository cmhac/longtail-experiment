"""Conflict persistence adapter for duplicate drift outcomes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StoredConflict:
    """Stored conflict details used for audit and operator triage."""

    conflict_id: str
    run_id: str
    source_key: str
    series_key: str
    reference_period_key: str
    existing_observation_ref: str
    incoming_record_ref: str
    conflict_type: str
    conflict_state: str


class InMemoryConflictRepository:
    """In-memory conflict adapter used by orchestration tests."""

    def __init__(self) -> None:
        self._conflicts: dict[str, StoredConflict] = {}

    def add_conflict(self, payload: StoredConflict) -> None:
        """Persist one conflict record."""
        self._conflicts[payload.conflict_id] = payload

    def list_conflicts(self, run_id: str | None = None) -> list[StoredConflict]:
        """List conflicts, optionally filtered by run identifier."""
        rows = list(self._conflicts.values())
        if run_id is None:
            return rows
        return [row for row in rows if row.run_id == run_id]
