"""US2 trigger-mode tests for scheduled and on-demand execution."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.run_coordinator import RunCoordinator
from src.orchestration.jobs.run_outcome_service import RunOutcomeService
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


def test_scheduled_trigger_executes_registered_sources() -> None:
    """Scheduled trigger should execute registered source workflows."""
    coordinator = RunCoordinator(
        workflow_registry=_build_registry(),
        source_lock_service=SourceLockService(),
        run_outcome_service=RunOutcomeService(),
    )

    result = coordinator.run(trigger_type="scheduled", requested_by="scheduler")

    assert result["trigger_type"] == "scheduled"
    assert result["outcome_state"] == "success"


def test_ondemand_trigger_executes_registered_sources() -> None:
    """On-demand trigger should execute registered source workflows."""
    coordinator = RunCoordinator(
        workflow_registry=_build_registry(),
        source_lock_service=SourceLockService(),
        run_outcome_service=RunOutcomeService(),
    )

    result = coordinator.run(trigger_type="on_demand", requested_by="operator")

    assert result["trigger_type"] == "on_demand"
    assert result["outcome_state"] == "success"
