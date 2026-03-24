"""Contract tests for FRED FEDFUNDS source workflow behavior."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any, Protocol

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.services.canonical_ingest_service import CanonicalIngestService
from src.orchestration.jobs.source_ingest_runner import SourceIngestRunner
from src.orchestration.jobs.sources.fred_fedfunds_source import (
    FRED_FEDFUNDS_CANONICAL_SERIES,
    FRED_FEDFUNDS_SERIES_ID,
    FRED_FEDFUNDS_SOURCE_KEY,
    FRED_GASREGW_CANONICAL_SERIES,
    FRED_GASREGW_SERIES_ID,
    build_fred_fedfunds_source_workflow,
)
from src.orchestration.jobs.workflow_registry import SourceWorkflowRegistry

TWO = 2


class _Observation(Protocol):
    series_key: object
    observed_on: object


class _CaptureRepository:
    def __init__(self) -> None:
        self.rows: list[_Observation] = []

    def upsert_observation(self, observation: _Observation) -> None:
        self.rows.append(observation)


class _CheckpointRepo:
    def __init__(self, latest_by_series: dict[str, date] | None = None) -> None:
        self._latest_by_series = latest_by_series or {}

    def read_latest_observed_on(self, *, series_key: str) -> date | None:
        return self._latest_by_series.get(series_key)


class _FakeClient:
    def __init__(
        self,
        rows_by_series: dict[str, list[dict[str, Any]]] | None = None,
        *,
        should_fail: bool = False,
        fail_series_ids: set[str] | None = None,
    ) -> None:
        self._rows_by_series = rows_by_series or {}
        self._should_fail = should_fail
        self._fail_series_ids = fail_series_ids or set()
        self.calls: list[dict[str, Any]] = []

    def fetch_observations(
        self,
        *,
        api_key: str,
        series_id: str,
        start_date: date | None,
    ) -> list[dict[str, Any]]:
        self.calls.append(
            {
                "api_key": api_key,
                "series_id": series_id,
                "start_date": start_date,
            }
        )
        if self._should_fail:
            raise RuntimeError("fred unavailable")
        if series_id in self._fail_series_ids:
            raise RuntimeError(f"fred unavailable for {series_id}")
        return self._rows_by_series.get(series_id, [])


def _build_registry(
    *,
    client: _FakeClient,
    checkpoint_latest_by_series: dict[str, date] | None = None,
) -> tuple[SourceWorkflowRegistry, _CaptureRepository]:
    capture_repo = _CaptureRepository()
    service = CanonicalIngestService(repository=capture_repo)
    runner = SourceIngestRunner(canonical_ingest_service=service)
    registry = SourceWorkflowRegistry()
    registry.register(
        build_fred_fedfunds_source_workflow(
            runner,
            observation_repository=_CheckpointRepo(checkpoint_latest_by_series),
            client=client,
        )
    )
    return registry, capture_repo


def test_fred_source_requires_credentials() -> None:
    """Missing credentials must raise immediately rather than returning a soft failure."""
    client = _FakeClient(rows_by_series={})
    registry, _capture_repo = _build_registry(client=client)

    with pytest.raises(EnvironmentError, match="FRED_API_KEY"):
        registry.execute_for_source(
            source_key=FRED_FEDFUNDS_SOURCE_KEY,
            run_id="run-fred-missing-key",
            trigger_type="on_demand",
            run_context={},
        )
    assert len(client.calls) == 0


def test_fred_source_maps_grouped_series_and_tracks_partial_success() -> None:
    """Grouped fetch should ingest both series while quarantining malformed records."""
    client = _FakeClient(
        rows_by_series={
            FRED_FEDFUNDS_SERIES_ID: [
                {"date": "2026-01-02", "value": "4.33", "realtime_end": "2026-01-03T00:00:00Z"},
                {"date": "2026-01-03", "value": ".", "realtime_end": "2026-01-04T00:00:00Z"},
            ],
            FRED_GASREGW_SERIES_ID: [
                {"date": "2026-01-04", "value": "3.22", "realtime_end": "2026-01-05T00:00:00Z"},
            ],
        }
    )
    registry, capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=FRED_FEDFUNDS_SOURCE_KEY,
        run_id="run-fred-partial",
        trigger_type="on_demand",
        run_context={"api_key": "test-key"},
    )

    assert result.status == "partial_success"
    assert result.accepted_count == TWO
    assert result.quarantined_count == 1
    assert result.failed_count == 0
    assert len(capture_repo.rows) == TWO
    assert len(client.calls) == TWO
    assert len(result.series_outcomes) == TWO

    fedfunds_outcome = next(
        outcome
        for outcome in result.series_outcomes
        if outcome["provider_series_id"] == FRED_FEDFUNDS_SERIES_ID
    )
    gas_outcome = next(
        outcome
        for outcome in result.series_outcomes
        if outcome["provider_series_id"] == FRED_GASREGW_SERIES_ID
    )
    assert fedfunds_outcome["status"] == "partial_success"
    assert fedfunds_outcome["accepted_count"] == 1
    assert fedfunds_outcome["quarantined_count"] == 1
    assert gas_outcome["status"] == "success"
    assert gas_outcome["accepted_count"] == 1


def test_fred_source_uses_incremental_start_date_from_latest_checkpoint() -> None:
    """Fetcher should compute incremental start dates independently per series."""
    client = _FakeClient(rows_by_series={})
    registry, _capture_repo = _build_registry(
        client=client,
        checkpoint_latest_by_series={
            FRED_FEDFUNDS_CANONICAL_SERIES: date(2026, 1, 5),
            FRED_GASREGW_CANONICAL_SERIES: date(2026, 1, 10),
        },
    )

    result = registry.execute_for_source(
        source_key=FRED_FEDFUNDS_SOURCE_KEY,
        run_id="run-fred-incremental",
        trigger_type="scheduled",
        run_context={"api_key": "test-key"},
    )

    assert result.status == "success"
    assert len(client.calls) == TWO
    start_by_series = {call["series_id"]: call["start_date"] for call in client.calls}
    assert start_by_series[FRED_FEDFUNDS_SERIES_ID] == date(2026, 1, 6)
    assert start_by_series[FRED_GASREGW_SERIES_ID] == date(2026, 1, 11)


def test_fred_source_reports_partial_failure_when_one_series_fails() -> None:
    """One failed series and one successful series should return partial success."""
    client = _FakeClient(
        rows_by_series={
            FRED_FEDFUNDS_SERIES_ID: [
                {"date": "2026-01-02", "value": "4.33", "realtime_end": "2026-01-03T00:00:00Z"},
            ],
        },
        fail_series_ids={FRED_GASREGW_SERIES_ID},
    )
    registry, _capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=FRED_FEDFUNDS_SOURCE_KEY,
        run_id="run-fred-provider-fail",
        trigger_type="on_demand",
        run_context={"api_key": "test-key"},
    )

    assert result.status == "partial_success"
    assert result.failed_count == 1
    assert result.accepted_count == 1
    assert result.outcome_reason_code is None
    assert len(result.series_outcomes) == TWO

    failed_outcome = next(
        outcome
        for outcome in result.series_outcomes
        if outcome["provider_series_id"] == FRED_GASREGW_SERIES_ID
    )
    assert failed_outcome["status"] == "failure"
    assert failed_outcome["outcome_reason_code"] == "provider_request_failed"


def test_fred_source_reports_failure_when_all_series_fail() -> None:
    """When all configured series fail provider retrieval, workflow returns failure."""
    client = _FakeClient(should_fail=True)
    registry, _capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=FRED_FEDFUNDS_SOURCE_KEY,
        run_id="run-fred-all-provider-fail",
        trigger_type="on_demand",
        run_context={"api_key": "test-key"},
    )

    assert result.status == "failure"
    assert result.failed_count == TWO
    assert result.accepted_count == 0
    assert result.quarantined_count == 0
    assert result.outcome_reason_code == "provider_request_failed"
    assert len(result.series_outcomes) == TWO
