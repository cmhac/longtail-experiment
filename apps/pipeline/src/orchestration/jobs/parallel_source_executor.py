"""Bounded parallel source execution with overlap-guard handling."""

from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from typing import Protocol

from .trend_errors import TrendProcessingError
from .workflow_result import SourceWorkflowResult


class SourceExecutionHandler(Protocol):
    """Protocol for executing one source workflow."""

    def __call__(self, source_key: str) -> SourceWorkflowResult:
        """Execute one source and return terminal result."""


class SourceLockProtocol(Protocol):
    """Protocol for source overlap guard operations."""

    def acquire(self, source_key: str, trigger_token: str) -> str:
        """Acquire lock state for one source and run token."""

    def release(self, source_key: str, active_run_id: str) -> str | None:
        """Release lock for one source and run token."""


@dataclass(frozen=True)
class ParallelExecutionSummary:
    """Execution results for one bounded run loop."""

    source_results: list[SourceWorkflowResult]
    max_active_observed: int


class ParallelSourceExecutor:
    """Execute due sources in deterministic bounded-concurrency batches."""

    def __init__(self, *, max_active_sources: int = 4) -> None:
        """Initialize executor with the maximum concurrent active-source limit."""
        if max_active_sources <= 0:
            raise ValueError("max_active_sources must be >= 1")
        self._max_active_sources = max_active_sources

    @property
    def max_active_sources(self) -> int:
        """Configured active-source ceiling for run execution."""
        return self._max_active_sources

    def execute(
        self,
        *,
        run_id: str,
        due_source_keys: list[str],
        source_lock_service: SourceLockProtocol,
        handler: SourceExecutionHandler,
    ) -> ParallelExecutionSummary:
        """Execute due sources with strict FIFO launch ordering and lock checks."""
        pending = list(due_source_keys)
        futures: dict[Future[SourceWorkflowResult], str] = {}
        source_results: list[SourceWorkflowResult] = []
        max_active_observed = 0

        with ThreadPoolExecutor(max_workers=self._max_active_sources) as executor:
            while pending or futures:
                while pending and len(futures) < self._max_active_sources:
                    source_key = pending.pop(0)
                    lock_status = source_lock_service.acquire(source_key, run_id)
                    if lock_status != "acquired":
                        source_results.append(
                            SourceWorkflowResult(
                                source_key=source_key,
                                status="deferred",
                                outcome_reason_code=f"overlap_guard_{lock_status}",
                                message="source execution deferred by overlap guard",
                            )
                        )
                        continue

                    future = executor.submit(self._run_one, handler, source_key)
                    futures[future] = source_key

                if not futures:
                    continue

                max_active_observed = max(max_active_observed, len(futures))
                done, _ = wait(set(futures.keys()), return_when=FIRST_COMPLETED)

                for future in done:
                    source_key = futures.pop(future)
                    try:
                        source_results.append(future.result())
                    finally:
                        source_lock_service.release(source_key, run_id)

        return ParallelExecutionSummary(
            source_results=source_results,
            max_active_observed=max_active_observed,
        )

    @staticmethod
    def _run_one(handler: SourceExecutionHandler, source_key: str) -> SourceWorkflowResult:
        try:
            return handler(source_key)
        except OSError:  # pragma: no cover - hard fail-fast: missing credentials/config
            raise
        except TrendProcessingError as exc:
            return SourceWorkflowResult(
                source_key=source_key,
                status="failure",
                failed_count=1,
                outcome_reason_code="trend_processing_failed",
                message=str(exc),
            )
        except Exception as exc:  # pragma: no cover - runtime protection path
            return SourceWorkflowResult(
                source_key=source_key,
                status="failure",
                failed_count=1,
                message=str(exc),
            )
