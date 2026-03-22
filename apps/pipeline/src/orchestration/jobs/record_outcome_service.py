"""Record-level outcome and run-context persistence service."""

from __future__ import annotations

from typing import Protocol

from .conflict_persistence_service import ConflictInput, ConflictPersistenceService
from .duplicate_drift_classifier import classify_duplicate_drift


class RunContextRepository(Protocol):
    """Protocol for run-context persistence behavior."""

    def add_run_context(self, *, run_id: str, context: dict[str, object]) -> None:
        """Persist run-context metadata for one run."""


class RecordOutcomeService:
    """Compute per-record outcomes and persist conflict details when needed."""

    def __init__(
        self,
        conflict_persistence_service: ConflictPersistenceService,
        run_context_repository: RunContextRepository | None = None,
    ) -> None:
        """Initialize outcome service dependencies."""
        self._conflict_service = conflict_persistence_service
        self._run_context_repository = run_context_repository

    def persist_run_context(self, run_id: str, context: dict[str, object]) -> None:
        """Persist run context metadata when a repository adapter is provided."""
        if self._run_context_repository is None:
            return
        self._run_context_repository.add_run_context(run_id=run_id, context=context)

    def resolve_record_outcome(
        self,
        *,
        run_id: str,
        source_key: str,
        reference_period_key: str,
        incoming: dict[str, object],
        existing: dict[str, object] | None,
    ) -> dict[str, object]:
        """Resolve and persist one record outcome."""
        state = classify_duplicate_drift(existing=existing, incoming=incoming)
        if state == "duplicate_no_op":
            return {"status": "duplicate_no_op", "conflict_id": None}
        if state == "conflict":
            existing_ref = "unknown"
            if existing is not None:
                existing_ref = str(existing.get("observation_ref", "unknown"))

            conflict = self._conflict_service.persist_conflict(
                ConflictInput(
                    run_id=run_id,
                    source_key=source_key,
                    series_key=str(incoming.get("series_key", "")),
                    reference_period_key=reference_period_key,
                    existing_observation_ref=existing_ref,
                    incoming_record_ref=str(incoming.get("record_ref", "incoming")),
                    conflict_type="value_mismatch",
                )
            )
            return {"status": "conflict", "conflict_id": conflict["conflict_id"]}

        return {"status": "accepted", "conflict_id": None}
