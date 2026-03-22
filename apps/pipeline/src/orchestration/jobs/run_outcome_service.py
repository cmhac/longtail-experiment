"""Run-level aggregation service for source workflow outcomes."""

from __future__ import annotations

from typing import TypedDict

from .workflow_result import SourceWorkflowResult


class RunOutcomeAggregate(TypedDict):
    """Typed aggregate counters and final run outcome state."""

    outcome_state: str
    accepted_count: int
    quarantined_count: int
    failed_count: int
    failed_source_count: int
    duplicate_no_op_count: int
    conflict_count: int
    due_source_count: int
    executed_source_count: int
    deferred_source_count: int
    not_due_source_count: int


class RunOutcomeService:
    """Aggregate source outcomes into one run summary payload."""

    def aggregate(self, source_results: list[SourceWorkflowResult]) -> RunOutcomeAggregate:
        """Compute run-level counters and terminal outcome state."""
        accepted = sum(result.accepted_count for result in source_results)
        quarantined = sum(result.quarantined_count for result in source_results)
        failed = sum(result.failed_count for result in source_results)
        duplicate_no_op = sum(result.duplicate_no_op_count for result in source_results)
        conflicts = sum(result.conflict_count for result in source_results)
        failed_source_count = sum(1 for result in source_results if result.status == "failure")

        executed_source_count = sum(
            1
            for result in source_results
            if result.status in {"success", "partial_success", "failure"}
        )
        deferred_source_count = sum(1 for result in source_results if result.status == "deferred")
        not_due_source_count = sum(1 for result in source_results if result.status == "not_due")
        due_source_count = executed_source_count + deferred_source_count

        has_success = any(
            result.status in {"success", "partial_success"} for result in source_results
        )
        has_failure = any(result.status == "failure" for result in source_results)
        if has_success and has_failure:
            outcome_state = "partial_success"
        elif has_failure:
            outcome_state = "failure"
        else:
            outcome_state = "success"

        return {
            "outcome_state": outcome_state,
            "accepted_count": accepted,
            "quarantined_count": quarantined,
            "failed_count": failed,
            "failed_source_count": failed_source_count,
            "duplicate_no_op_count": duplicate_no_op,
            "conflict_count": conflicts,
            "due_source_count": due_source_count,
            "executed_source_count": executed_source_count,
            "deferred_source_count": deferred_source_count,
            "not_due_source_count": not_due_source_count,
        }
