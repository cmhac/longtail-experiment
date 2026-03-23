"""Regression tests for post-cutover source outcome persistence."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import cast

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
from src.orchestration.runtime import map_source_outcomes_to_persistence_records


class _CaptureRepository:
    def __init__(self) -> None:
        self.payloads: list[dict[str, object]] = []

    def add_run_outcome(self, payload) -> None:
        self.payloads.append(payload)


def _registry() -> SourceWorkflowRegistry:
    registry = SourceWorkflowRegistry()
    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-post-cutover",
            source_key="post-cutover-source",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=lambda request: SourceWorkflowResult(
                source_key=request.source_key,
                status="success",
                accepted_count=1,
            ),
        )
    )
    return registry


def test_post_cutover_run_persists_current_source_outcomes_only() -> None:
    """Runtime should persist source outcomes produced by the current run."""
    repository = _CaptureRepository()
    coordinator = RunCoordinator(
        workflow_registry=_registry(),
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
        run_repository=repository,
    )

    coordinator.run(trigger_type="on_demand", requested_by="operator")

    assert len(repository.payloads) == 1
    persisted = repository.payloads[0]
    assert persisted["run_id"]
    source_results = cast(list[dict[str, object]], persisted["source_results"])
    assert len(source_results) == 1
    assert source_results[0]["source_key"] == "post-cutover-source"


def test_runtime_maps_source_outcomes_to_persistence_view_records() -> None:
    """Runtime mapping should preserve persistence-relevant outcome metadata."""
    mapped = map_source_outcomes_to_persistence_records(
        [
            {
                "source_key": "post-cutover-source",
                "status": "failure",
                "outcome_reason_code": "provider_request_failed",
                "message": "timeout",
                "visible_in_dagit": True,
                "failure_summary": "provider_request_failed: timeout",
            }
        ]
    )

    assert mapped == [
        {
            "source_key": "post-cutover-source",
            "state": "failure",
            "outcome_reason_code": "provider_request_failed",
            "message": "timeout",
            "visible_in_dagit": True,
            "failure_summary": "provider_request_failed: timeout",
            "series_outcomes": [],
        }
    ]
