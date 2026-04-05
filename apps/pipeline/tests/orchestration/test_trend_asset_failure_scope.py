"""US1 tests for source-branch-scoped failure mapping of trend execution."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.parallel_source_executor import ParallelSourceExecutor
from src.orchestration.jobs.source_ingest_runner import _is_true_irregular_cadence_failure
from src.orchestration.jobs.trend_errors import TrendProcessingError
from src.orchestration.jobs.workflow_result import SourceWorkflowResult
from src.orchestration.resources.source_lock_service import SourceLockService


def test_trend_failure_maps_to_branch_scoped_reason_and_other_sources_continue() -> None:
    """One trend-processing failure should stay isolated to the affected source branch."""
    executor = ParallelSourceExecutor(max_active_sources=2)
    lock_service = SourceLockService()

    def _handler(source_key: str) -> SourceWorkflowResult:
        if source_key == "source-b":
            raise TrendProcessingError("seasonality_changed")
        return SourceWorkflowResult(source_key=source_key, status="success", accepted_count=1)

    summary = executor.execute(
        run_id="run-trend-failure-scope",
        due_source_keys=["source-a", "source-b", "source-c"],
        source_lock_service=lock_service,
        handler=_handler,
    )

    by_source = {result.source_key: result for result in summary.source_results}
    assert by_source["source-b"].status == "failure"
    assert by_source["source-b"].outcome_reason_code == "trend_processing_failed"
    assert by_source["source-a"].status == "success"
    assert by_source["source-c"].status == "success"


def test_true_irregular_cadence_rejection_is_mapped_to_trend_processing_failed() -> None:
    """Irregular cadence rejection should remain branch-scoped trend-processing failure."""
    executor = ParallelSourceExecutor(max_active_sources=2)
    lock_service = SourceLockService()

    def _handler(source_key: str) -> SourceWorkflowResult:
        if source_key == "source-b":
            raise TrendProcessingError("irregular_spacing irregular_gap_ratio_exceeds_threshold")
        return SourceWorkflowResult(source_key=source_key, status="success", accepted_count=1)

    summary = executor.execute(
        run_id="run-trend-irregular-scope",
        due_source_keys=["source-a", "source-b", "source-c"],
        source_lock_service=lock_service,
        handler=_handler,
    )

    by_source = {result.source_key: result for result in summary.source_results}
    assert by_source["source-b"].status == "failure"
    assert by_source["source-b"].outcome_reason_code == "trend_processing_failed"
    assert by_source["source-a"].status == "success"
    assert by_source["source-c"].status == "success"


def test_true_irregular_cadence_detection_helper() -> None:
    """Helper should identify true irregular rejection reason codes only."""
    assert _is_true_irregular_cadence_failure(
        {
            "cadence_state": "irregular_rejected",
            "reason_code": "irregular_gap_ratio_exceeds_threshold",
        }
    )
    assert not _is_true_irregular_cadence_failure(
        {
            "cadence_state": "gap_tolerant",
            "reason_code": "isolated_irregular_gaps_tolerated",
        }
    )
