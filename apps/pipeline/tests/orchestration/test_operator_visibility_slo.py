"""Operator visibility SLO test for run outcome availability."""

from __future__ import annotations

import sys
from datetime import timedelta
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
            workflow_id="wf-visibility",
            source_key="bls",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_handler,
        )
    )
    return registry


def test_operator_visibility_is_under_five_minutes() -> None:
    """Run summary timestamps should become visible within five minutes."""
    coordinator = RunCoordinator(
        workflow_registry=_build_registry(),
        source_lock_service=SourceLockService(),
        run_outcome_service=RunOutcomeService(),
    )

    payload = coordinator.run(trigger_type="scheduled", requested_by="scheduler")
    latency = payload["completed_at"] - payload["started_at"]

    assert latency <= timedelta(minutes=5)
