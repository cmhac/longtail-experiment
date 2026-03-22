"""Conflict persistence service for duplicate drift mismatches."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4


@dataclass(frozen=True)
class ConflictInput:
    """Input payload for conflict row persistence."""

    run_id: str
    source_key: str
    series_key: str
    reference_period_key: str
    existing_observation_ref: str
    incoming_record_ref: str
    conflict_type: str


class ConflictRepository(Protocol):
    """Protocol for conflict persistence adapter behavior."""

    def add_conflict(self, payload: dict[str, object]) -> None:
        """Persist one conflict payload."""


class ConflictPersistenceService:
    """Persist conflict rows for audit and governance workflows."""

    def __init__(self, repository: ConflictRepository | None) -> None:
        """Initialize service with a conflict repository adapter."""
        self._repository = repository

    def persist_conflict(self, payload: ConflictInput) -> dict[str, object]:
        """Persist one conflict row and return the normalized payload."""
        row: dict[str, object] = {
            "conflict_id": f"conf-{uuid4().hex[:12]}",
            "run_id": payload.run_id,
            "source_key": payload.source_key,
            "series_key": payload.series_key,
            "reference_period_key": payload.reference_period_key,
            "existing_observation_ref": payload.existing_observation_ref,
            "incoming_record_ref": payload.incoming_record_ref,
            "conflict_type": payload.conflict_type,
            "conflict_state": "open",
            "created_at": datetime.now(tz=UTC),
            "resolved_at": None,
        }
        if self._repository is not None:
            self._repository.add_conflict(row)
        return row
