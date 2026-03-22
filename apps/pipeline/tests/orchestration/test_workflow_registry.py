"""Unit tests for source workflow registry behavior."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.workflow_registry import (
    SourceWorkflowRegistration,
    SourceWorkflowRegistry,
)
from src.orchestration.jobs.workflow_request import SourceWorkflowRequest
from src.orchestration.jobs.workflow_result import (
    SourceWorkflowResult,
    map_dagit_failure_category,
)


def _handler(request: SourceWorkflowRequest) -> SourceWorkflowResult:
    return SourceWorkflowResult(source_key=request.source_key, status="success", accepted_count=1)


def test_registry_registers_and_executes_source_workflow() -> None:
    """Registry should execute a registered source handler successfully."""
    registry = SourceWorkflowRegistry()
    registration = SourceWorkflowRegistration(
        workflow_id="wf-bls",
        source_key="bls",
        owner="pipeline",
        supported_trigger_modes={"scheduled", "on_demand"},
        handler=_handler,
    )

    registry.register(registration)
    result = registry.execute(
        SourceWorkflowRequest(
            run_id="run-1",
            source_key="bls",
            trigger_type="scheduled",
            run_context={"requested_by": "system"},
        )
    )

    assert result.status == "success"
    assert result.accepted_count == 1


def test_registry_rejects_duplicate_active_source_key() -> None:
    """Registry should reject duplicate source-key registration."""
    registry = SourceWorkflowRegistry()
    registration = SourceWorkflowRegistration(
        workflow_id="wf-bls",
        source_key="bls",
        owner="pipeline",
        supported_trigger_modes={"scheduled"},
        handler=_handler,
    )
    registry.register(registration)

    with pytest.raises(ValueError):
        registry.register(registration)


def test_registry_rejects_unknown_source_execution() -> None:
    """Registry should fail for execution requests with unknown sources."""
    registry = SourceWorkflowRegistry()

    with pytest.raises(KeyError):
        registry.execute(
            SourceWorkflowRequest(
                run_id="run-1",
                source_key="missing",
                trigger_type="scheduled",
                run_context={},
            )
        )


def test_map_dagit_failure_category_for_missing_prerequisites() -> None:
    """Prerequisite probe failure should map to prerequisite_missing category."""
    assert (
        map_dagit_failure_category(
            prerequisites_ready=False,
            endpoint_reachable=False,
            workspace_loaded=False,
        )
        == "prerequisite_missing"
    )


def test_map_dagit_failure_category_for_unreachable_endpoint() -> None:
    """Endpoint probe failure should map to endpoint_unavailable category."""
    assert (
        map_dagit_failure_category(
            prerequisites_ready=True,
            endpoint_reachable=False,
            workspace_loaded=False,
        )
        == "endpoint_unavailable"
    )


def test_map_dagit_failure_category_for_workspace_load_failure() -> None:
    """Loaded endpoint with missing workspace should map to workspace_load_failed category."""
    assert (
        map_dagit_failure_category(
            prerequisites_ready=True,
            endpoint_reachable=True,
            workspace_loaded=False,
        )
        == "workspace_load_failed"
    )


def test_map_dagit_failure_category_for_fallback_partial_environment() -> None:
    """Unexpected degraded state should map to partial_environment category."""
    assert (
        map_dagit_failure_category(
            prerequisites_ready=True,
            endpoint_reachable=True,
            workspace_loaded=True,
        )
        == "partial_environment"
    )
