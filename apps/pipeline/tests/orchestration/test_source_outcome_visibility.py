"""Integration tests for source-level outcome visibility metadata."""

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
from src.orchestration.runtime import map_source_outcomes_to_persistence_records


def _build_registry() -> SourceWorkflowRegistry:
    registry = SourceWorkflowRegistry()

    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-success",
            source_key="visible-success",
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
            workflow_id="wf-failure",
            source_key="visible-failure",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=lambda request: SourceWorkflowResult(
                source_key=request.source_key,
                status="failure",
                failed_count=1,
                outcome_reason_code="provider_request_failed",
                message="provider timeout",
            ),
        )
    )
    return registry


def test_source_outcomes_include_visibility_for_success_and_failure() -> None:
    """Both success and failure outcomes should carry source visibility metadata."""
    coordinator = RunCoordinator(
        workflow_registry=_build_registry(),
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
    )

    payload = coordinator.run(trigger_type="on_demand", requested_by="operator")
    by_source = {row["source_key"]: row for row in payload["source_results"]}

    assert by_source["visible-success"]["visible_in_dagit"] is True
    assert by_source["visible-success"]["failure_summary"] is None
    assert by_source["visible-failure"]["visible_in_dagit"] is True
    assert "provider_request_failed" in str(by_source["visible-failure"]["failure_summary"])


def test_source_schedule_trigger_attribution_in_outcomes() -> None:
    """Feature 011 US2: source outcomes should carry trigger attribution for scheduled runs."""
    coordinator = RunCoordinator(
        workflow_registry=_build_registry(),
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
    )

    payload = coordinator.run(
        trigger_type="scheduled",
        requested_by="visible-success_schedule",
        source_keys=["visible-success"],
    )

    assert payload["trigger_type"] == "scheduled"
    assert payload["requested_by"] == "visible-success_schedule"
    assert len(payload["source_results"]) == 1
    assert payload["source_results"][0]["source_key"] == "visible-success"
    assert payload["source_results"][0]["visible_in_dagit"] is True


def test_series_outcome_traceability_persists_across_ownership_transition() -> None:
    """Series outcomes should remain explicitly traceable when ownership mode changes."""
    grouped_records = map_source_outcomes_to_persistence_records(
        [
            {
                "source_key": "fred_fedfunds",
                "status": "success",
                "series_outcomes": [
                    {
                        "series_item_key": "fred_gasregw",
                        "status": "success",
                        "owner_adapter_key": "fred_fedfunds",
                        "ownership_mode": "grouped",
                    }
                ],
            }
        ]
    )
    split_records = map_source_outcomes_to_persistence_records(
        [
            {
                "source_key": "fred_gasregw",
                "status": "success",
                "series_outcomes": [
                    {
                        "series_item_key": "fred_gasregw",
                        "status": "success",
                        "owner_adapter_key": "fred_gasregw",
                        "ownership_mode": "split",
                    }
                ],
            }
        ]
    )

    assert grouped_records[0]["series_outcomes"][0]["series_item_key"] == "fred_gasregw"
    assert split_records[0]["series_outcomes"][0]["series_item_key"] == "fred_gasregw"
