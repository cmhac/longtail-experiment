"""US2 trigger-mode tests for scheduled and on-demand execution."""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.due_source_selector import DueSourceSelector
from src.orchestration.jobs.parallel_source_executor import ParallelSourceExecutor
from src.orchestration.jobs.run_coordinator import RunCoordinator
from src.orchestration.jobs.source_assets.ownership_mode import SeriesOwnershipModeRecord
from src.orchestration.jobs.source_assets.series_catalog import SeriesCatalogEntry
from src.orchestration.jobs.source_schedule_policy import SourceSchedulePolicy
from src.orchestration.jobs.workflow_registry import (
    SourceWorkflowRegistration,
    SourceWorkflowRegistry,
)
from src.orchestration.jobs.workflow_result import SourceWorkflowResult
from src.orchestration.resources.source_lock_service import SourceLockService


def _build_registry() -> SourceWorkflowRegistry:
    registry = SourceWorkflowRegistry()

    def _handler(request):
        return SourceWorkflowResult(
            source_key=request.source_key,
            status="success",
            accepted_count=1,
        )

    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-1",
            source_key="bls",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_handler,
        )
    )
    return registry


class _RunRepository:
    def __init__(self) -> None:
        self.schedule_policies: dict[str, dict[str, object]] = {}

    def read_all_schedule_policies(self) -> dict[str, dict[str, object]]:
        return self.schedule_policies


def test_scheduled_trigger_executes_registered_sources() -> None:
    """Scheduled trigger should execute registered source workflows."""
    coordinator = RunCoordinator(
        workflow_registry=_build_registry(),
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
    )

    result = coordinator.run(trigger_type="scheduled", requested_by="scheduler")

    assert result["trigger_type"] == "scheduled"
    assert result["outcome_state"] == "success"


def test_ondemand_trigger_executes_registered_sources() -> None:
    """On-demand trigger should execute registered source workflows."""
    coordinator = RunCoordinator(
        workflow_registry=_build_registry(),
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
    )

    result = coordinator.run(trigger_type="on_demand", requested_by="operator")

    assert result["trigger_type"] == "on_demand"
    assert result["outcome_state"] == "success"


def test_scheduled_trigger_marks_fred_not_due_when_recent_success_exists() -> None:
    """Scheduled trigger should skip FRED when persisted cadence window is still active."""
    registry = SourceWorkflowRegistry()

    def _handler(request):
        return SourceWorkflowResult(
            source_key=request.source_key,
            status="success",
            accepted_count=1,
        )

    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-fred",
            source_key="fred_fedfunds",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_handler,
            schedule_policy=SourceSchedulePolicy(
                source_key="fred_fedfunds",
                cadence_type="daily",
            ),
        )
    )

    run_repo = _RunRepository()
    run_repo.schedule_policies = {
        "fred_fedfunds": {
            "source_key": "fred_fedfunds",
            "last_successful_at": datetime.now(tz=UTC) - timedelta(hours=1),
        }
    }

    coordinator = RunCoordinator(
        workflow_registry=registry,
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
        run_repository=run_repo,
    )

    result = coordinator.run(trigger_type="scheduled", requested_by="scheduler")

    assert result["executed_source_count"] == 0
    assert result["not_due_source_count"] == 1
    assert result["source_results"][0]["source_key"] == "fred_fedfunds"
    assert result["source_results"][0]["status"] == "not_due"


def test_source_schedule_trigger_carries_attribution() -> None:
    """Feature 011 US2: per-source schedule trigger should carry source attribution."""
    coordinator = RunCoordinator(
        workflow_registry=_build_registry(),
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
    )

    result = coordinator.run(
        trigger_type="scheduled",
        requested_by="bls_schedule",
        source_keys=["bls"],
    )

    assert result["trigger_type"] == "scheduled"
    assert result["requested_by"] == "bls_schedule"
    assert result["executed_source_count"] == 1
    assert result["source_results"][0]["source_key"] == "bls"


def test_source_schedule_trigger_preserves_run_id_attribution() -> None:
    """Feature 011 US2: run_id must be present in source-scheduled trigger output."""
    coordinator = RunCoordinator(
        workflow_registry=_build_registry(),
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
    )

    result = coordinator.run(
        trigger_type="scheduled",
        requested_by="bls_schedule",
        source_keys=["bls"],
    )

    assert result["run_id"] is not None
    assert len(result["run_id"]) > 0


def test_series_level_trigger_origin_is_preserved_for_source_execution() -> None:
    """Series-level on-demand trigger should preserve operator attribution metadata."""
    coordinator = RunCoordinator(
        workflow_registry=_build_registry(),
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
    )

    result = coordinator.run(
        trigger_type="on_demand",
        requested_by="operator:fred_fedfunds",
        source_keys=["bls"],
        series_item_keys=["fred_fedfunds"],
    )

    assert result["requested_by"] == "operator:fred_fedfunds"
    assert result["trigger_origin"] == "operator:fred_fedfunds"


def test_grouped_split_coexistence_uses_authoritative_owner_for_schedule() -> None:
    """When grouped and split owners coexist, schedule guard should avoid duplicate execution."""
    registry = SourceWorkflowRegistry()

    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-fred-grouped",
            source_key="fred_fedfunds",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=lambda request: SourceWorkflowResult(
                source_key=request.source_key,
                status="success",
                accepted_count=1,
            ),
        )
    )
    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-fred-gasregw",
            source_key="fred_gasregw",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=lambda request: SourceWorkflowResult(
                source_key=request.source_key,
                status="success",
                accepted_count=1,
            ),
        )
    )

    coordinator = RunCoordinator(
        workflow_registry=registry,
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
        series_catalog_entries=(
            SeriesCatalogEntry(
                source_key="fred_fedfunds",
                provider_group_key="fred",
                series_item_key="fred_gasregw",
                canonical_series_key="ENERGY.US.GASREGW",
                ownership_mode="grouped",
            ),
            SeriesCatalogEntry(
                source_key="fred_gasregw",
                provider_group_key="fred",
                series_item_key="fred_gasregw",
                canonical_series_key="ENERGY.US.GASREGW",
                ownership_mode="split",
            ),
        ),
        ownership_mode_registry={
            "fred_gasregw": SeriesOwnershipModeRecord(
                series_item_key="fred_gasregw",
                owner_adapter_key="fred_gasregw",
                mode="split",
            )
        },
    )

    result = coordinator.run(trigger_type="scheduled", requested_by="scheduler")
    source_keys = [row["source_key"] for row in result["source_results"]]
    assert "fred_gasregw" in source_keys
    assert "fred_fedfunds" not in source_keys
