"""US2 partial-success run aggregation tests."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.run_outcome_service import RunOutcomeService
from src.orchestration.jobs.workflow_result import SourceWorkflowResult

EXPECTED_ACCEPTED = 3
EXPECTED_FAILED = 1


def test_partial_success_when_mixed_source_results_exist() -> None:
    """Mixed success and failure source results should produce partial success."""
    service = RunOutcomeService()

    summary = service.aggregate(
        [
            SourceWorkflowResult(source_key="bls", status="success", accepted_count=3),
            SourceWorkflowResult(source_key="fred", status="failure", failed_count=1),
        ]
    )

    assert summary["outcome_state"] == "partial_success"
    assert summary["accepted_count"] == EXPECTED_ACCEPTED
    assert summary["failed_count"] == EXPECTED_FAILED
