"""Coordinator for scheduled and on-demand orchestration runs."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, Literal, TypedDict, cast
from uuid import uuid4

from src.orchestration.resources.source_lock_service import SourceLockService

from .due_source_selector import DueSourceSelector, SourceEligibilityDecision
from .parallel_source_executor import ParallelSourceExecutor
from .run_outcome_service import RunOutcomeService
from .workflow_registry import SourceWorkflowRegistration, SourceWorkflowRegistry
from .workflow_result import SourceWorkflowResult


class RunSummary(TypedDict):
    """Typed run summary emitted by coordinator execution."""

    run_id: str
    trigger_type: str
    requested_by: str
    started_at: datetime
    completed_at: datetime
    source_results: list[dict[str, object]]
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


class RunCoordinator:
    """Execute all registered source workflows and aggregate run outcomes."""

    def __init__(
        self,
        *,
        workflow_registry: SourceWorkflowRegistry,
        source_lock_service: SourceLockService,
        due_source_selector: DueSourceSelector,
        parallel_source_executor: ParallelSourceExecutor,
        run_repository: object | None = None,
    ) -> None:
        """Initialize coordinator with registry, lock, aggregation, and persistence dependencies."""
        self._workflow_registry = workflow_registry
        self._source_lock_service = source_lock_service
        self._run_outcome_service = RunOutcomeService()
        self._due_source_selector = due_source_selector
        self._parallel_source_executor = parallel_source_executor
        self._run_repository = run_repository

    def run(
        self,
        *,
        trigger_type: Literal["scheduled", "on_demand"],
        requested_by: str,
        source_keys: list[str] | None = None,
    ) -> RunSummary:
        """Execute one orchestration run and return summary details."""
        run_id = str(uuid4())
        started_at = datetime.now(tz=UTC)
        registrations = self._filter_registrations(source_keys)

        eligibility_decisions = self._build_eligibility_decisions(
            trigger_type=trigger_type,
            registrations=registrations,
            source_keys=source_keys,
            evaluated_at=started_at,
        )

        due_source_keys = [
            decision.source_key
            for decision in eligibility_decisions
            if decision.eligibility_state == "due" and decision.selected_for_execution
        ]

        execution = self._parallel_source_executor.execute(
            run_id=run_id,
            due_source_keys=due_source_keys,
            source_lock_service=self._source_lock_service,
            handler=lambda source_key: self._workflow_registry.execute_for_source(
                source_key=source_key,
                run_id=run_id,
                trigger_type=trigger_type,
                run_context={"requested_by": requested_by},
            ),
        )

        non_due_results = self._build_non_due_results(eligibility_decisions)
        source_results = execution.source_results + non_due_results
        source_results.sort(key=lambda result: result.source_key)

        aggregate = self._run_outcome_service.aggregate(source_results)
        completed_at = datetime.now(tz=UTC)
        payload: RunSummary = {
            "run_id": run_id,
            "trigger_type": trigger_type,
            "requested_by": requested_by,
            "started_at": started_at,
            "completed_at": completed_at,
            "source_results": [result.model_dump() for result in source_results],
            "outcome_state": aggregate["outcome_state"],
            "accepted_count": aggregate["accepted_count"],
            "quarantined_count": aggregate["quarantined_count"],
            "failed_count": aggregate["failed_count"],
            "failed_source_count": aggregate["failed_source_count"],
            "duplicate_no_op_count": aggregate["duplicate_no_op_count"],
            "conflict_count": aggregate["conflict_count"],
            "due_source_count": aggregate["due_source_count"],
            "executed_source_count": aggregate["executed_source_count"],
            "deferred_source_count": aggregate["deferred_source_count"],
            "not_due_source_count": aggregate["not_due_source_count"],
        }
        if self._run_repository is not None:
            add_run_outcome = getattr(self._run_repository, "add_run_outcome", None)
            if callable(add_run_outcome):
                typed_add_run_outcome = cast(Callable[[RunSummary], None], add_run_outcome)
                typed_add_run_outcome(payload)

            write_snapshots = getattr(
                self._run_repository,
                "write_eligibility_snapshots",
                None,
            )
            if callable(write_snapshots):
                typed_write_snapshots = cast(Callable[..., Any], write_snapshots)
                typed_write_snapshots(
                    run_id=run_id,
                    snapshots=[
                        self._decision_to_snapshot(decision) for decision in eligibility_decisions
                    ],
                )
        return payload

    def _filter_registrations(
        self,
        source_keys: list[str] | None,
    ) -> list[SourceWorkflowRegistration]:
        registrations = self._workflow_registry.list_registrations()
        if source_keys is None:
            return registrations
        requested = set(source_keys)
        return [
            registration for registration in registrations if registration.source_key in requested
        ]

    def _build_eligibility_decisions(
        self,
        *,
        trigger_type: Literal["scheduled", "on_demand"],
        registrations: list[SourceWorkflowRegistration],
        source_keys: list[str] | None,
        evaluated_at: datetime,
    ) -> list[SourceEligibilityDecision]:
        if trigger_type == "scheduled":
            return self._due_source_selector.evaluate_scheduled(
                registrations=registrations,
                evaluated_at=evaluated_at,
            )

        selected = source_keys or [registration.source_key for registration in registrations]
        return self._due_source_selector.evaluate_on_demand(
            source_keys=selected,
            evaluated_at=evaluated_at,
        )

    def _build_non_due_results(
        self,
        decisions: list[SourceEligibilityDecision],
    ) -> list[SourceWorkflowResult]:
        results: list[SourceWorkflowResult] = []
        for decision in decisions:
            if decision.selected_for_execution:
                continue
            results.append(
                SourceWorkflowResult(
                    source_key=decision.source_key,
                    status="not_due",
                    outcome_reason_code=decision.reason_code,
                    message=f"source not selected for execution ({decision.reason_code})",
                )
            )
        return results

    @staticmethod
    def _decision_to_snapshot(decision: SourceEligibilityDecision) -> dict[str, object]:
        return {
            "source_key": decision.source_key,
            "eligibility_state": decision.eligibility_state,
            "reason_code": decision.reason_code,
            "evaluated_at": decision.evaluated_at,
            "due_at": decision.due_at,
            "selected_for_execution": decision.selected_for_execution,
        }
