"""US3 run visibility and aggregate consistency tests."""

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


class _NowAnchoredSelector(DueSourceSelector):
    def __init__(self, now: datetime) -> None:
        super().__init__()
        self._now = now

    def evaluate_scheduled(self, *, registrations, evaluated_at):
        return super().evaluate_scheduled(registrations=registrations, evaluated_at=self._now)


class _CaptureRepository:
    def __init__(self) -> None:
        self.payload: dict[str, object] | None = None
        self.snapshots: list[dict[str, object]] = []

    def add_run_outcome(self, payload) -> None:
        self.payload = payload

    def write_eligibility_snapshots(
        self,
        *,
        run_id: str,
        snapshots: list[dict[str, object]],
    ) -> None:
        self.snapshots = [{**snapshot, "run_id": run_id} for snapshot in snapshots]


def _registry(now: datetime) -> SourceWorkflowRegistry:
    registry = SourceWorkflowRegistry()

    def _success(request):
        return SourceWorkflowResult(
            source_key=request.source_key,
            status="success",
            accepted_count=1,
        )

    def _failure(request):
        return SourceWorkflowResult(source_key=request.source_key, status="failure", failed_count=1)

    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-success",
            source_key="source-success",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_success,
            schedule_policy=SourceSchedulePolicy(
                source_key="source-success",
                cadence_type="hourly",
                last_successful_at=now - timedelta(hours=2),
            ),
        )
    )
    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-failure",
            source_key="source-failure",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_failure,
            schedule_policy=SourceSchedulePolicy(
                source_key="source-failure",
                cadence_type="hourly",
                last_successful_at=now - timedelta(hours=2),
            ),
        )
    )
    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-not-due",
            source_key="source-not-due",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_success,
            schedule_policy=SourceSchedulePolicy(
                source_key="source-not-due",
                cadence_type="daily",
                last_successful_at=now - timedelta(hours=1),
            ),
        )
    )
    return registry


def test_source_eligibility_and_outcome_audit_contract() -> None:
    """Scheduled runs should capture both eligibility decisions and terminal source outcomes."""
    now = datetime(2026, 3, 21, 12, 0, tzinfo=UTC)
    repository = _CaptureRepository()
    coordinator = RunCoordinator(
        workflow_registry=_registry(now),
        source_lock_service=SourceLockService(),
        due_source_selector=_NowAnchoredSelector(now),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
        run_repository=repository,
    )

    payload = coordinator.run(trigger_type="scheduled", requested_by="scheduler")

    assert repository.payload is not None
    assert repository.snapshots
    assert {snapshot["source_key"] for snapshot in repository.snapshots} == {
        "source-success",
        "source-failure",
        "source-not-due",
    }

    by_source = {row["source_key"]: row for row in payload["source_results"]}
    assert by_source["source-success"]["status"] == "success"
    assert by_source["source-failure"]["status"] == "failure"
    assert by_source["source-not-due"]["status"] == "not_due"


def test_run_aggregate_counts_match_source_classifications() -> None:
    """Run-level counters should equal the sum of source-level state classifications."""
    now = datetime(2026, 3, 21, 12, 0, tzinfo=UTC)
    coordinator = RunCoordinator(
        workflow_registry=_registry(now),
        source_lock_service=SourceLockService(),
        due_source_selector=_NowAnchoredSelector(now),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
    )

    payload = coordinator.run(trigger_type="scheduled", requested_by="scheduler")
    statuses = [row["status"] for row in payload["source_results"]]

    executed = sum(1 for status in statuses if status in {"success", "partial_success", "failure"})
    deferred = statuses.count("deferred")
    not_due = statuses.count("not_due")

    assert payload["executed_source_count"] == executed
    assert payload["deferred_source_count"] == deferred
    assert payload["not_due_source_count"] == not_due
    assert payload["due_source_count"] == executed + deferred


def test_historical_artifacts_do_not_drive_scheduling_decisions() -> None:
    """Feature 011 US3: legacy cadence policy should not affect per-source schedule runs."""
    now = datetime(2026, 3, 21, 12, 0, tzinfo=UTC)
    coordinator = RunCoordinator(
        workflow_registry=_registry(now),
        source_lock_service=SourceLockService(),
        due_source_selector=_NowAnchoredSelector(now),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
    )

    # Per-source schedule trigger with explicit source_keys bypasses due evaluation
    payload = coordinator.run(
        trigger_type="scheduled",
        requested_by="source-success_schedule",
        source_keys=["source-success"],
    )

    # All explicitly-targeted sources execute regardless of legacy policy state
    assert payload["executed_source_count"] == 1
    assert payload["not_due_source_count"] == 0
    assert payload["source_results"][0]["source_key"] == "source-success"
    assert payload["source_results"][0]["status"] == "success"
