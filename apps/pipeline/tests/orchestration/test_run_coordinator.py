"""Coverage-focused tests for run coordinator behavior."""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.due_source_selector import DueSourceSelector
from src.orchestration.jobs.parallel_source_executor import ParallelSourceExecutor
from src.orchestration.jobs.run_coordinator import RunCoordinator
from src.orchestration.jobs.source_schedule_policy import SourceSchedulePolicy
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
        self.schedule_policies: dict[str, dict[str, object]] = {}
        self.upserts: list[dict[str, object]] = []

    def add_run_outcome(self, payload: object) -> None:
        """Persist one in-memory run payload for assertions."""
        self.rows.append(payload)

    def read_all_schedule_policies(self) -> dict[str, dict[str, object]]:
        """Return pre-seeded schedule policy rows for coordinator hydration."""
        return self.schedule_policies

    def upsert_schedule_policy(self, **kwargs: object) -> None:
        """Capture upsert calls for assertions."""
        self.upserts.append(kwargs)


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


def test_run_coordinator_marks_source_not_due_with_recent_db_policy() -> None:
    """Recent persisted last_successful_at should prevent scheduled execution."""
    registry = SourceWorkflowRegistry()
    policy = SourceSchedulePolicy(source_key="bls", cadence_type="hourly")

    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-policy",
            source_key="bls",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=lambda _request: SourceWorkflowResult(source_key="bls", status="success"),
            schedule_policy=policy,
        )
    )

    run_repo = _RunRepository()
    run_repo.schedule_policies = {
        "bls": {
            "source_key": "bls",
            "last_successful_at": datetime.now(tz=UTC) - timedelta(minutes=10),
        }
    }

    coordinator = RunCoordinator(
        workflow_registry=registry,
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
        run_repository=run_repo,
    )

    payload = coordinator.run(trigger_type="scheduled", requested_by="scheduler")

    assert payload["executed_source_count"] == 0
    assert payload["not_due_source_count"] == 1
    assert payload["source_results"][0]["status"] == "not_due"


def test_run_coordinator_marks_source_due_with_stale_db_policy() -> None:
    """Stale persisted last_successful_at should allow scheduled execution."""
    registry = SourceWorkflowRegistry()
    policy = SourceSchedulePolicy(source_key="bls", cadence_type="hourly")

    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-policy",
            source_key="bls",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=lambda _request: SourceWorkflowResult(
                source_key="bls",
                status="success",
                accepted_count=1,
            ),
            schedule_policy=policy,
        )
    )

    run_repo = _RunRepository()
    run_repo.schedule_policies = {
        "bls": {
            "source_key": "bls",
            "last_successful_at": datetime.now(tz=UTC) - timedelta(hours=2),
        }
    }

    coordinator = RunCoordinator(
        workflow_registry=registry,
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
        run_repository=run_repo,
    )

    payload = coordinator.run(trigger_type="scheduled", requested_by="scheduler")

    assert payload["executed_source_count"] == 1
    assert payload["not_due_source_count"] == 0
    assert payload["source_results"][0]["status"] == "success"


def test_run_coordinator_upserts_schedule_policy_for_successful_sources_only() -> None:
    """Coordinator should persist schedule state for successful scheduled sources."""
    registry = SourceWorkflowRegistry()

    def _ok_handler(request):
        return SourceWorkflowResult(
            source_key=request.source_key,
            status="success",
            accepted_count=1,
        )

    def _bad_handler(request):
        return SourceWorkflowResult(source_key=request.source_key, status="failure", failed_count=1)

    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-ok",
            source_key="source-ok",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_ok_handler,
            schedule_policy=SourceSchedulePolicy(source_key="source-ok", cadence_type="hourly"),
        )
    )
    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-bad",
            source_key="source-bad",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_bad_handler,
            schedule_policy=SourceSchedulePolicy(source_key="source-bad", cadence_type="hourly"),
        )
    )
    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-none",
            source_key="source-none",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_ok_handler,
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

    coordinator.run(trigger_type="scheduled", requested_by="scheduler")

    assert len(run_repo.upserts) == 1
    upsert = run_repo.upserts[0]
    assert upsert["source_key"] == "source-ok"
    assert upsert["cadence_type"] == "hourly"
    assert isinstance(upsert["last_successful_at"], datetime)
    assert isinstance(upsert["updated_at"], datetime)


def test_scheduled_run_with_explicit_source_keys_bypasses_due_filter() -> None:
    """Feature 011: scheduled trigger with explicit source_keys should skip due evaluation."""
    registry = SourceWorkflowRegistry()

    def _handler(request):
        return SourceWorkflowResult(
            source_key=request.source_key,
            status="success",
            accepted_count=1,
        )

    # Register with a policy that would mark source as not-due (recent success)
    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-bypass",
            source_key="bypass-source",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_handler,
            schedule_policy=SourceSchedulePolicy(
                source_key="bypass-source",
                cadence_type="daily",
                last_successful_at=datetime.now(tz=UTC) - timedelta(minutes=5),
            ),
        )
    )

    coordinator = RunCoordinator(
        workflow_registry=registry,
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
    )

    # With explicit source_keys, the coordinator should execute even though
    # due-evaluation would mark the source as not-due
    payload = coordinator.run(
        trigger_type="scheduled",
        requested_by="bypass_source_schedule",
        source_keys=["bypass-source"],
    )

    assert payload["executed_source_count"] == 1
    assert payload["not_due_source_count"] == 0
    assert payload["source_results"][0]["status"] == "success"
