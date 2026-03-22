"""Contract tests for source workflow request/result schemas."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.workflow_request import SourceWorkflowRequest
from src.orchestration.jobs.workflow_result import SourceWorkflowResult

EXPECTED_DUPLICATE_NO_OP = 2
EXPECTED_CONFLICTS = 1


def test_workflow_request_requires_contract_fields() -> None:
    """Workflow request schema should accept required contract fields."""
    request = SourceWorkflowRequest(
        run_id="run-1",
        source_key="bls",
        trigger_type="scheduled",
        run_context={"window": "2026-01"},
    )

    assert request.source_key == "bls"
    assert request.trigger_type == "scheduled"


def test_workflow_result_rejects_negative_counts() -> None:
    """Workflow result schema should enforce non-negative counters."""
    with pytest.raises(ValidationError):
        SourceWorkflowResult(
            source_key="bls",
            status="failure",
            accepted_count=-1,
        )


def test_workflow_result_supports_duplicate_and_conflict_counters() -> None:
    """Workflow result should preserve duplicate and conflict counters."""
    result = SourceWorkflowResult(
        source_key="bls",
        status="partial_success",
        accepted_count=5,
        quarantined_count=1,
        failed_count=1,
        duplicate_no_op_count=2,
        conflict_count=1,
    )

    assert result.duplicate_no_op_count == EXPECTED_DUPLICATE_NO_OP
    assert result.conflict_count == EXPECTED_CONFLICTS
