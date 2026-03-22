"""Coverage-focused tests for run coordinator behavior."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.due_source_selector import DueSourceSelector
from src.orchestration.jobs.parallel_source_executor import ParallelSourceExecutor
from src.orchestration.jobs.run_coordinator import RunCoordinator
from src.orchestration.jobs.workflow_registry import (
    SourceWorkflowRegistration,
    SourceWorkflowRegistry,
)
from src.orchestration.jobs.workflow_result import SourceWorkflowResult
from src.orchestration.resources.source_lock_service import SourceLockService

EXPECTED_ACCEPTED_COUNT = 2


class _RunRepository:
    def __init__(self) -> None:
        self.rows: list[object] = []

    def add_run_outcome(self, payload: object) -> None:
        """Persist one in-memory run payload for assertions."""
        self.rows.append(payload)


def test_run_coordinator_persists_successful_summary() -> None:
    """Coordinator should persist run summary for successful source execution."""
    registry = SourceWorkflowRegistry()

    def _handler(request):
        return SourceWorkflowResult(
            source_key=request.source_key,
            status="success",
            accepted_count=EXPECTED_ACCEPTED_COUNT,
        )

    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-ok",
            source_key="bls",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_handler,
        )
    )
    run_repo = _RunRepository()
    coordinator = RunCoordinator(
        workflow_registry=registry,
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
        run_repository=run_repo,
    )

    payload = coordinator.run(trigger_type="scheduled", requested_by="scheduler")

    assert payload["outcome_state"] == "success"
    assert payload["accepted_count"] == EXPECTED_ACCEPTED_COUNT
    assert len(run_repo.rows) == 1


def test_run_coordinator_marks_source_failure_when_handler_raises() -> None:
    """Coordinator should continue and capture failure details when one source crashes."""
    registry = SourceWorkflowRegistry()

    def _bad_handler(_request):
        raise RuntimeError("source exploded")

    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-bad",
            source_key="bad-source",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_bad_handler,
        )
    )
    coordinator = RunCoordinator(
        workflow_registry=registry,
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
    )

    payload = coordinator.run(trigger_type="on_demand", requested_by="operator")

    assert payload["outcome_state"] == "failure"
    assert payload["failed_count"] == 1


def test_run_coordinator_deduplicated_lock_state_is_reported_as_failure() -> None:
    """Coordinator should record failure when lock service deduplicates an active+queued source."""
    registry = SourceWorkflowRegistry()

    def _handler(request):
        return SourceWorkflowResult(
            source_key=request.source_key,
            status="success",
            accepted_count=1,
        )

    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-lock",
            source_key="bls",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_handler,
        )
    )
    lock_service = SourceLockService()
    lock_service.acquire("bls", "run-active")
    lock_service.acquire("bls", "run-queued")

    coordinator = RunCoordinator(
        workflow_registry=registry,
        source_lock_service=lock_service,
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
    )

    payload = coordinator.run(trigger_type="scheduled", requested_by="scheduler")

    assert payload["outcome_state"] == "success"
    assert payload["deferred_source_count"] == 1
    assert payload["source_results"][0]["status"] == "deferred"
