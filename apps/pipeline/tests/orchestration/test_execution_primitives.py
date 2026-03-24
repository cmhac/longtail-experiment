"""Coverage-oriented tests for execution primitives and scheduling helpers."""

from __future__ import annotations

import sys
from datetime import UTC
from pathlib import Path
from typing import cast

import pytest
from dagster import build_op_context

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.parallel_source_executor import ParallelSourceExecutor
from src.orchestration.jobs.source_assets.triggering import build_invalid_source_request_summary
from src.orchestration.jobs.workflow_registry import (
    SourceWorkflowRegistration,
    SourceWorkflowRegistry,
)
from src.orchestration.jobs.workflow_request import SourceWorkflowRequest
from src.orchestration.jobs.workflow_result import SourceWorkflowResult
from src.orchestration.resources.source_lock_service import SourceLockService
from src.orchestration.schedules.source_asset_schedules import _make_source_schedule
from src.orchestration.source_asset_definitions import (
    _run_series_item,
    _run_single_source,
    fred_fedfunds_source_asset,
    fred_gasregw_source_asset,
)


class _Resources:
    def __init__(self) -> None:
        self.run_coordinator = _Coordinator()


class _Context:
    def __init__(self) -> None:
        self.resources = _Resources()


class _Coordinator:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def run(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "run_id": "run-1",
            "outcome_state": "success",
            "executed_source_count": 1,
            "failed_source_count": 0,
        }


def test_source_lock_service_acquire_release_and_snapshot_paths() -> None:
    """Lock service should cover acquire, queue, dedupe, promote, and no-op release paths."""
    lock_service = SourceLockService()

    assert lock_service.acquire("fred", "run-1") == "acquired"
    assert lock_service.acquire("fred", "run-2") == "queued"
    assert lock_service.acquire("fred", "run-3") == "deduplicated"

    snapshot = lock_service.snapshot("fred")
    assert snapshot.source_key == "fred"
    assert snapshot.active_run_id == "run-1"
    assert snapshot.queued_trigger_token == "run-2"
    assert snapshot.lock_updated_at.tzinfo == UTC

    promoted = lock_service.release("fred", "run-1")
    assert promoted == "run-2"

    assert lock_service.release("fred", "run-2") is None
    assert lock_service.release("fred", "run-3") is None


def test_parallel_executor_handles_success_failure_and_deferred_paths() -> None:
    """Parallel executor should emit success, deferred, and failure source results."""
    lock_service = SourceLockService()
    lock_service.acquire("deferred-source", "run-123")
    lock_service.acquire("deferred-source", "queued-123")

    executor = ParallelSourceExecutor(max_active_sources=2)

    def _handler(source_key: str) -> SourceWorkflowResult:
        if source_key == "boom-source":
            raise RuntimeError("exploded")
        return SourceWorkflowResult(
            source_key=source_key,
            status="success",
            accepted_count=1,
        )

    summary = executor.execute(
        run_id="run-123",
        due_source_keys=["ok-source", "deferred-source", "boom-source"],
        source_lock_service=lock_service,
        handler=_handler,
    )

    by_source = {result.source_key: result for result in summary.source_results}
    assert by_source["ok-source"].status == "success"
    assert by_source["deferred-source"].status == "deferred"
    assert by_source["boom-source"].status == "failure"
    assert summary.max_active_observed >= 1


def test_workflow_registry_rejects_invalid_registration_and_trigger_modes() -> None:
    """Workflow registry should enforce registration and trigger-mode contract rules."""
    registry = SourceWorkflowRegistry()

    with pytest.raises(ValueError, match="only active workflows"):
        registry.register(
            SourceWorkflowRegistration(
                workflow_id="wf-inactive",
                source_key="inactive",
                owner="pipeline",
                supported_trigger_modes={"on_demand"},
                status="inactive",
                handler=lambda request: SourceWorkflowResult(
                    source_key=request.source_key,
                    status="success",
                ),
            )
        )

    registration = SourceWorkflowRegistration(
        workflow_id="wf-source",
        source_key="source-a",
        owner="pipeline",
        supported_trigger_modes={"on_demand"},
        handler=lambda request: SourceWorkflowResult(
            source_key=request.source_key,
            status="success",
        ),
    )
    registry.register(registration)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(registration)

    with pytest.raises(KeyError, match="unknown source workflow"):
        registry.execute_for_source(
            source_key="missing",
            run_id="run-1",
            trigger_type="on_demand",
            run_context={},
        )

    with pytest.raises(ValueError, match="trigger type is not supported"):
        registry.execute(
            SourceWorkflowRequest(
                run_id="run-1",
                source_key="source-a",
                trigger_type="scheduled",
                run_context={},
            )
        )

    result = registry.execute_for_source(
        source_key="source-a",
        run_id="run-1",
        trigger_type="on_demand",
        run_context={},
    )
    assert result.status == "success"
    assert registry.list_source_keys() == ["source-a"]
    assert registry.list_registrations()[0].source_key == "source-a"


def test_schedule_factory_emits_series_and_provider_tags() -> None:
    """Schedule factory should populate provider-group and series selection tags."""
    schedule_def = _make_source_schedule("fred_fedfunds", "0 0 * * *", "daily")
    run_request = schedule_def(None)

    assert run_request.tags["source_keys"] == "fred_fedfunds"
    assert run_request.tags["provider_group_key"] == "fred"
    assert run_request.tags["series_item_keys"] == "fred_fedfunds,fred_gasregw"


def test_source_asset_helpers_run_source_and_series_variants() -> None:
    """Source- and series-scoped helper invocations should map to expected output keys."""
    context = _Context()

    source_result = _run_single_source(context=context, source_key="fred_fedfunds")
    series_result = _run_series_item(
        context=context,
        source_key="fred_fedfunds",
        series_item_key="fred_gasregw",
    )

    assert source_result["source_key"] == "fred_fedfunds"
    assert series_result["series_item_key"] == "fred_gasregw"


def test_source_asset_wrapper_assets_delegate_to_helpers() -> None:
    """Public asset wrappers should delegate to the internal run helpers."""
    context = build_op_context(resources={"run_coordinator": _Coordinator()})
    fedfunds_result = cast(dict[str, object], fred_fedfunds_source_asset(context))
    gas_result = cast(dict[str, object], fred_gasregw_source_asset(context))

    assert fedfunds_result["series_item_key"] == "fred_fedfunds"
    assert gas_result["series_item_key"] == "fred_gasregw"


def test_invalid_source_request_summary_contains_expected_counters() -> None:
    """Invalid source request summary should surface deterministic failure counters."""
    summary = build_invalid_source_request_summary(
        requested_by="operator",
        trigger_type="on_demand",
        invalid_source_keys=["unknown-source"],
        available_source_keys=["fred_fedfunds"],
    )

    assert summary["outcome_state"] == "failure"
    assert summary["failed_source_count"] == 1
    source_results = cast(list[dict[str, object]], summary["source_results"])
    assert source_results[0]["outcome_reason_code"] == "invalid_source_key"
