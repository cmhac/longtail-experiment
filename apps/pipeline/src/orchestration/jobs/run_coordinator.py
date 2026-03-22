"""Coordinator for scheduled and on-demand orchestration runs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal, Protocol, TypedDict
from uuid import uuid4

from src.orchestration.resources.source_lock_service import SourceLockService

from .run_outcome_service import RunOutcomeService
from .workflow_registry import SourceWorkflowRegistry
from .workflow_result import SourceWorkflowResult


class RunRepository(Protocol):
    """Protocol for persisting run summary payloads."""

    def add_run_outcome(self, payload: RunSummary) -> None:
        """Persist one run summary payload."""


class RunSummary(TypedDict):
    """Typed run summary emitted by coordinator execution."""

    run_id: str
    trigger_type: str
    requested_by: str
    started_at: datetime
    completed_at: datetime
    source_results: list[dict[str, object]]
    outcome_state: str
    accepted_count: int
    quarantined_count: int
    failed_count: int
    duplicate_no_op_count: int
    conflict_count: int


class RunCoordinator:
    """Execute all registered source workflows and aggregate run outcomes."""

    def __init__(
        self,
        *,
        workflow_registry: SourceWorkflowRegistry,
        source_lock_service: SourceLockService,
        run_outcome_service: RunOutcomeService,
        run_repository: RunRepository | None = None,
    ) -> None:
        """Initialize coordinator with registry, lock, aggregation, and persistence dependencies."""
        self._workflow_registry = workflow_registry
        self._source_lock_service = source_lock_service
        self._run_outcome_service = run_outcome_service
        self._run_repository = run_repository

    def run(
        self,
        *,
        trigger_type: Literal["scheduled", "on_demand"],
        requested_by: str,
        source_keys: list[str] | None = None,
    ) -> RunSummary:
        """Execute one orchestration run and return summary details."""
        run_id = str(uuid4())
        keys = source_keys or self._workflow_registry.list_source_keys()
        source_results: list[SourceWorkflowResult] = []
        started_at = datetime.now(tz=UTC)

        for source_key in keys:
            lock_status = self._source_lock_service.acquire(source_key, run_id)
            if lock_status == "deduplicated":
                source_results.append(
                    SourceWorkflowResult(
                        source_key=source_key,
                        status="failure",
                        failed_count=1,
                        message="source trigger deduplicated while active+queued",
                    )
                )
                continue

            try:
                source_results.append(
                    self._workflow_registry.execute_for_source(
                        source_key=source_key,
                        run_id=run_id,
                        trigger_type=trigger_type,
                        run_context={"requested_by": requested_by},
                    )
                )
            except Exception as exc:  # pragma: no cover - fail-open policy boundary
                source_results.append(
                    SourceWorkflowResult(
                        source_key=source_key,
                        status="failure",
                        failed_count=1,
                        message=str(exc),
                    )
                )
            finally:
                self._source_lock_service.release(source_key, run_id)

        aggregate = self._run_outcome_service.aggregate(source_results)
        completed_at = datetime.now(tz=UTC)
        payload: RunSummary = {
            "run_id": run_id,
            "trigger_type": trigger_type,
            "requested_by": requested_by,
            "started_at": started_at,
            "completed_at": completed_at,
            "source_results": [result.model_dump() for result in source_results],
            "outcome_state": aggregate["outcome_state"],
            "accepted_count": aggregate["accepted_count"],
            "quarantined_count": aggregate["quarantined_count"],
            "failed_count": aggregate["failed_count"],
            "duplicate_no_op_count": aggregate["duplicate_no_op_count"],
            "conflict_count": aggregate["conflict_count"],
        }
        if self._run_repository is not None:
            self._run_repository.add_run_outcome(payload)
        return payload
