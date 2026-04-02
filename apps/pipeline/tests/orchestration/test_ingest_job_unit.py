"""Unit tests for ingest job op behavior and edge cases."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.ingest_job import execute_ingest_run
from src.orchestration.jobs.source_assets.authority_state import SchedulingAuthorityState
from src.orchestration.jobs.source_assets.series_catalog import SeriesCatalogEntry

INVALID_SOURCE_FAILURE_COUNT = 2


class _Coordinator:
    def __init__(self, summary: dict[str, object] | None = None) -> None:
        self.calls: list[dict[str, object]] = []
        self._summary = summary or {
            "run_id": "run-1",
            "outcome_state": "success",
            "accepted_count": 1,
            "due_source_count": 1,
            "executed_source_count": 1,
            "deferred_source_count": 0,
            "not_due_source_count": 0,
            "failed_source_count": 0,
            "source_results": [{"source_key": "fred", "status": "success"}],
        }

    def list_registered_source_keys(self) -> list[str]:
        return ["bls", "fred"]

    def run(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(kwargs)
        return dict(self._summary)


class _Log:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str, dict[str, object] | None]] = []

    def error(self, message: str, extra: dict[str, object] | None = None) -> None:
        self.messages.append(("error", message, extra))

    def info(self, message: str, extra: dict[str, object] | None = None) -> None:
        self.messages.append(("info", message, extra))

    def warning(self, message: str, extra: dict[str, object] | None = None) -> None:
        self.messages.append(("warning", message, extra))


class _Context:
    def __init__(self, *, resources: dict[str, object], tags: dict[str, str]) -> None:
        self.resources = SimpleNamespace(**resources)
        self.run = SimpleNamespace(tags=tags)
        self.log = _Log()


def _series_catalog() -> tuple[SeriesCatalogEntry, ...]:
    return (
        SeriesCatalogEntry(
            source_key="fred",
            provider_group_key="fred",
            series_item_key="fred_fedfunds",
            canonical_series_key="INT.US.FEDFUNDS",
        ),
    )


def _authority() -> SchedulingAuthorityState:
    return SchedulingAuthorityState(
        authority_mode="dagster_only",
        legacy_paths_disabled=True,
        partial_failure_mode=False,
        cutover_completed_at=datetime.now(tz=UTC),
    )


def _invoke_execute_ingest_run(context: _Context) -> dict[str, object]:
    compute_fn = cast(Any, execute_ingest_run.compute_fn)
    decorated_fn = cast(Any, getattr(compute_fn, "decorated_fn", compute_fn))
    return cast(dict[str, object], decorated_fn(context))


def test_execute_ingest_run_rejects_invalid_requested_keys() -> None:
    """Invalid source/series keys should return fail-fast summary without coordinator run."""
    coordinator = _Coordinator()
    context = _Context(
        resources={
            "run_coordinator": coordinator,
            "scheduling_authority_state": _authority(),
            "series_catalog_entries": _series_catalog(),
        },
        tags={
            "trigger_type": "on_demand",
            "requested_by": "unit-test",
            "source_key": "unknown-source",
            "series_item_key": "unknown_series",
        },
    )

    result = _invoke_execute_ingest_run(context)

    assert result["outcome_state"] == "failure"
    assert result["failed_source_count"] == INVALID_SOURCE_FAILURE_COUNT
    assert coordinator.calls == []


def test_execute_ingest_run_includes_recovery_plan_on_failed_sources() -> None:
    """Failed source runs should attach post-cutover recovery plan metadata."""
    coordinator = _Coordinator(
        summary={
            "run_id": "run-2",
            "outcome_state": "partial_success",
            "accepted_count": 1,
            "due_source_count": 2,
            "executed_source_count": 2,
            "deferred_source_count": 0,
            "not_due_source_count": 0,
            "failed_source_count": 1,
            "source_results": [
                {"source_key": "fred", "status": "success"},
                {"source_key": "bls", "status": "failure"},
            ],
        }
    )
    context = _Context(
        resources={
            "run_coordinator": coordinator,
            "scheduling_authority_state": _authority(),
            "series_catalog_entries": _series_catalog(),
        },
        tags={"trigger_type": "scheduled", "requested_by": "unit-test"},
    )

    result = _invoke_execute_ingest_run(context)

    assert result["run_id"] == "run-2"
    assert result["failed_source_count"] == 1
    assert "recovery_plan" in result
    assert isinstance(result["recovery_plan"], dict)
    recovery = cast(dict[str, object], result["recovery_plan"])
    assert recovery["authority_mode"] == "dagster_only"
    assert recovery["failed_sources"] == ["bls"]


def test_execute_ingest_run_logs_warning_when_deferred_sources_present() -> None:
    """Deferred source count should emit warning branch for carry-forward visibility."""
    coordinator = _Coordinator(
        summary={
            "run_id": "run-3",
            "outcome_state": "partial_success",
            "accepted_count": 1,
            "due_source_count": 2,
            "executed_source_count": 1,
            "deferred_source_count": 1,
            "not_due_source_count": 0,
            "failed_source_count": 0,
            "source_results": [{"source_key": "fred", "status": "success"}],
        }
    )
    context = _Context(
        resources={
            "run_coordinator": coordinator,
            "scheduling_authority_state": _authority(),
            "series_catalog_entries": _series_catalog(),
        },
        tags={"trigger_type": "scheduled", "requested_by": "unit-test"},
    )

    result = _invoke_execute_ingest_run(context)

    assert result["deferred_source_count"] == 1
    warning_messages = [entry for entry in context.log.messages if entry[0] == "warning"]
    assert len(warning_messages) == 1
