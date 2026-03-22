"""US2 trigger-mode integration tests for due-source scheduling behavior."""

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
        self.snapshots: list[dict[str, object]] = []

    def add_run_outcome(self, _payload) -> None:
        pass

    def write_eligibility_snapshots(
        self,
        *,
        run_id: str,
        snapshots: list[dict[str, object]],
    ) -> None:
        self.snapshots = [{**snapshot, "run_id": run_id} for snapshot in snapshots]


def _build_registry(now: datetime) -> SourceWorkflowRegistry:
    registry = SourceWorkflowRegistry()

    def _handler(request):
        return SourceWorkflowResult(
            source_key=request.source_key,
            status="success",
            accepted_count=1,
        )

    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-due",
            source_key="due-source",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_handler,
            schedule_policy=SourceSchedulePolicy(
                source_key="due-source",
                cadence_type="hourly",
                last_successful_at=now - timedelta(hours=2),
            ),
        )
    )
    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-not-due",
            source_key="not-due-source",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_handler,
            schedule_policy=SourceSchedulePolicy(
                source_key="not-due-source",
                cadence_type="daily",
                last_successful_at=now - timedelta(hours=2),
            ),
        )
    )
    return registry


def test_scheduled_runs_execute_due_sources_only() -> None:
    """Scheduled trigger should execute only due sources and snapshot non-due decisions."""
    now = datetime(2026, 3, 21, 12, 0, tzinfo=UTC)
    repository = _CaptureRepository()
    coordinator = RunCoordinator(
        workflow_registry=_build_registry(now),
        source_lock_service=SourceLockService(),
        due_source_selector=_NowAnchoredSelector(now),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
        run_repository=repository,
    )

    payload = coordinator.run(trigger_type="scheduled", requested_by="scheduler")

    by_source = {row["source_key"]: row for row in payload["source_results"]}
    assert by_source["due-source"]["status"] == "success"
    assert by_source["not-due-source"]["status"] == "not_due"
    assert payload["due_source_count"] == 1
    assert payload["not_due_source_count"] == 1


def test_on_demand_subset_bypasses_due_state() -> None:
    """On-demand selected subsets should execute even when cadence says not due."""
    now = datetime(2026, 3, 21, 12, 0, tzinfo=UTC)
    coordinator = RunCoordinator(
        workflow_registry=_build_registry(now),
        source_lock_service=SourceLockService(),
        due_source_selector=_NowAnchoredSelector(now),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
    )

    payload = coordinator.run(
        trigger_type="on_demand",
        requested_by="operator",
        source_keys=["not-due-source"],
    )

    assert payload["due_source_count"] == 1
    assert payload["executed_source_count"] == 1
    by_source = {row["source_key"]: row for row in payload["source_results"]}
    assert by_source["not-due-source"]["status"] == "success"


def test_per_source_schedule_triggers_independently() -> None:
    """Feature 011 US1: per-source schedule should trigger only the owning source."""
    now = datetime(2026, 3, 21, 12, 0, tzinfo=UTC)
    repository = _CaptureRepository()
    coordinator = RunCoordinator(
        workflow_registry=_build_registry(now),
        source_lock_service=SourceLockService(),
        due_source_selector=_NowAnchoredSelector(now),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
        run_repository=repository,
    )

    # Simulate per-source schedule for "due-source" only
    payload = coordinator.run(
        trigger_type="scheduled",
        requested_by="due-source_schedule",
        source_keys=["due-source"],
    )

    assert payload["executed_source_count"] == 1
    assert payload["not_due_source_count"] == 0
    assert len(payload["source_results"]) == 1
    assert payload["source_results"][0]["source_key"] == "due-source"
    assert payload["source_results"][0]["status"] == "success"


def test_per_source_schedule_does_not_trigger_other_sources() -> None:
    """Feature 011 US1: triggering one source schedule must not execute other sources."""
    now = datetime(2026, 3, 21, 12, 0, tzinfo=UTC)
    coordinator = RunCoordinator(
        workflow_registry=_build_registry(now),
        source_lock_service=SourceLockService(),
        due_source_selector=_NowAnchoredSelector(now),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
    )

    payload = coordinator.run(
        trigger_type="scheduled",
        requested_by="not-due-source_schedule",
        source_keys=["not-due-source"],
    )

    source_keys = [r["source_key"] for r in payload["source_results"]]
    assert source_keys == ["not-due-source"]
    assert "due-source" not in source_keys
