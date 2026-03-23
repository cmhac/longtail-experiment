"""Foundational tests for source registration contract validation."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.source_assets.contracts import (
    SourceAssetContractError,
    register_source_assets,
)
from src.orchestration.jobs.workflow_registry import (
    SourceWorkflowRegistration,
    SourceWorkflowRegistry,
)
from src.orchestration.jobs.workflow_result import SourceWorkflowResult


def _handler(request):
    return SourceWorkflowResult(source_key=request.source_key, status="success", accepted_count=1)


def test_register_source_assets_rejects_duplicate_source_keys() -> None:
    """Duplicate source keys should be rejected before registry registration."""
    duplicate_registrations = [
        (
            "tests.first",
            SourceWorkflowRegistration(
                workflow_id="wf-1",
                source_key="dup",
                owner="pipeline",
                supported_trigger_modes={"scheduled", "on_demand"},
                handler=_handler,
            ),
        ),
        (
            "tests.second",
            SourceWorkflowRegistration(
                workflow_id="wf-2",
                source_key="dup",
                owner="pipeline",
                supported_trigger_modes={"scheduled", "on_demand"},
                handler=_handler,
            ),
        ),
    ]

    with pytest.raises(SourceAssetContractError, match="duplicate source_key"):
        register_source_assets(
            registry=SourceWorkflowRegistry(),
            registrations=duplicate_registrations,
        )


def test_register_source_assets_rejects_inactive_registration() -> None:
    """Inactive registrations should fail contract validation before register."""
    inactive_registration = [
        (
            "tests.inactive",
            SourceWorkflowRegistration(
                workflow_id="wf-inactive",
                source_key="inactive_source",
                owner="pipeline",
                supported_trigger_modes={"scheduled", "on_demand"},
                handler=_handler,
                status="inactive",
            ),
        )
    ]

    with pytest.raises(SourceAssetContractError, match="registration must be active"):
        register_source_assets(
            registry=SourceWorkflowRegistry(),
            registrations=inactive_registration,
        )


def test_register_source_assets_rejects_empty_workflow_id() -> None:
    """Registrations must include a non-empty workflow identifier."""
    invalid_registration = [
        (
            "tests.empty_workflow",
            SourceWorkflowRegistration(
                workflow_id="",
                source_key="empty_workflow_source",
                owner="pipeline",
                supported_trigger_modes={"scheduled", "on_demand"},
                handler=_handler,
            ),
        )
    ]

    with pytest.raises(SourceAssetContractError, match="workflow_id must be non-empty"):
        register_source_assets(
            registry=SourceWorkflowRegistry(),
            registrations=invalid_registration,
        )
