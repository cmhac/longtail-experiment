"""US1 bounded parallel execution and failure isolation tests."""

from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.parallel_source_executor import ParallelSourceExecutor
from src.orchestration.jobs.workflow_result import SourceWorkflowResult
from src.orchestration.resources.source_lock_service import SourceLockService

MAX_ACTIVE_SOURCES = 2
TOTAL_DUE_SOURCES = 6


def test_parallel_executor_never_exceeds_max_active_source_limit() -> None:
    """Executor should cap concurrent active sources to the configured max value."""
    executor = ParallelSourceExecutor(max_active_sources=MAX_ACTIVE_SOURCES)
    lock_service = SourceLockService()

    active = 0
    observed_max = 0
    guard = threading.Lock()

    def _handler(source_key: str) -> SourceWorkflowResult:
        nonlocal active, observed_max
        with guard:
            active += 1
            observed_max = max(observed_max, active)
        time.sleep(0.05)
        with guard:
            active -= 1
        return SourceWorkflowResult(source_key=source_key, status="success", accepted_count=1)

    summary = executor.execute(
        run_id="run-us1-ceiling",
        due_source_keys=[f"source-{index}" for index in range(TOTAL_DUE_SOURCES)],
        source_lock_service=lock_service,
        handler=_handler,
    )

    assert observed_max <= MAX_ACTIVE_SOURCES
    assert summary.max_active_observed <= MAX_ACTIVE_SOURCES
    assert len(summary.source_results) == TOTAL_DUE_SOURCES


def test_parallel_executor_isolates_source_failures() -> None:
    """One failing source should not prevent remaining due sources from completing."""
    executor = ParallelSourceExecutor(max_active_sources=3)
    lock_service = SourceLockService()

    def _handler(source_key: str) -> SourceWorkflowResult:
        if source_key == "source-2":
            raise RuntimeError("boom")
        return SourceWorkflowResult(source_key=source_key, status="success", accepted_count=1)

    summary = executor.execute(
        run_id="run-us1-failure-isolation",
        due_source_keys=["source-1", "source-2", "source-3"],
        source_lock_service=lock_service,
        handler=_handler,
    )

    by_source = {result.source_key: result for result in summary.source_results}
    assert by_source["source-2"].status == "failure"
    assert by_source["source-1"].status == "success"
    assert by_source["source-3"].status == "success"


def test_parallel_executor_fifo_order_with_single_slot_contention() -> None:
    """A single execution slot should preserve strict FIFO launch ordering."""
    executor = ParallelSourceExecutor(max_active_sources=1)
    lock_service = SourceLockService()
    launch_order: list[str] = []

    def _handler(source_key: str) -> SourceWorkflowResult:
        launch_order.append(source_key)
        return SourceWorkflowResult(source_key=source_key, status="success", accepted_count=1)

    summary = executor.execute(
        run_id="run-us1-fifo",
        due_source_keys=["source-a", "source-b", "source-c"],
        source_lock_service=lock_service,
        handler=_handler,
    )

    assert launch_order == ["source-a", "source-b", "source-c"]
    assert [result.source_key for result in summary.source_results] == [
        "source-a",
        "source-b",
        "source-c",
    ]
