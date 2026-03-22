"""Contract tests for FRED FEDFUNDS source workflow behavior."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any, Protocol

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.services.canonical_ingest_service import CanonicalIngestService
from src.orchestration.jobs.source_ingest_runner import SourceIngestRunner
from src.orchestration.jobs.sources.fred_fedfunds_source import (
    FRED_FEDFUNDS_CANONICAL_SERIES,
    FRED_FEDFUNDS_SERIES_ID,
    FRED_FEDFUNDS_SOURCE_KEY,
    build_fred_fedfunds_source_workflow,
)
from src.orchestration.jobs.workflow_registry import SourceWorkflowRegistry


class _Observation(Protocol):
    series_key: object
    observed_on: object


class _CaptureRepository:
    def __init__(self) -> None:
        self.rows: list[_Observation] = []

    def upsert_observation(self, observation: _Observation) -> None:
        self.rows.append(observation)


class _CheckpointRepo:
    def __init__(self, latest: date | None = None) -> None:
        self._latest = latest

    def read_latest_observed_on(self, *, series_key: str) -> date | None:
        assert series_key == FRED_FEDFUNDS_CANONICAL_SERIES
        return self._latest


class _FakeClient:
    def __init__(
        self, rows: list[dict[str, Any]] | None = None, *, should_fail: bool = False
    ) -> None:
        self._rows = rows or []
        self._should_fail = should_fail
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
        return self._rows


def _build_registry(
    *, client: _FakeClient, checkpoint_latest: date | None = None
) -> tuple[SourceWorkflowRegistry, _CaptureRepository]:
    capture_repo = _CaptureRepository()
    service = CanonicalIngestService(repository=capture_repo)
    runner = SourceIngestRunner(canonical_ingest_service=service)
    registry = SourceWorkflowRegistry()
    registry.register(
        build_fred_fedfunds_source_workflow(
            runner,
            observation_repository=_CheckpointRepo(checkpoint_latest),
            client=client,
        )
    )
    return registry, capture_repo


def test_fred_source_requires_credentials() -> None:
    """Missing credentials should fail with explicit reason code."""
    client = _FakeClient(rows=[])
    registry, _capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=FRED_FEDFUNDS_SOURCE_KEY,
        run_id="run-fred-missing-key",
        trigger_type="on_demand",
        run_context={},
    )

    assert result.status == "failure"
    assert result.failed_count == 1
    assert result.outcome_reason_code == "missing_credentials"
    assert len(client.calls) == 0


def test_fred_source_maps_provider_rows_and_tracks_partial_success() -> None:
    """Valid records should ingest while malformed values are quarantined."""
    client = _FakeClient(
        rows=[
            {"date": "2026-01-02", "value": "4.33", "realtime_end": "2026-01-03T00:00:00Z"},
            {"date": "2026-01-03", "value": ".", "realtime_end": "2026-01-04T00:00:00Z"},
        ]
    )
    registry, capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=FRED_FEDFUNDS_SOURCE_KEY,
        run_id="run-fred-partial",
        trigger_type="on_demand",
        run_context={"api_key": "test-key"},
    )

    assert result.status == "partial_success"
    assert result.accepted_count == 1
    assert result.quarantined_count == 1
    assert len(capture_repo.rows) == 1


def test_fred_source_uses_incremental_start_date_from_latest_checkpoint() -> None:
    """Fetcher should start at latest persisted date + 1 day when available."""
    client = _FakeClient(rows=[])
    registry, _capture_repo = _build_registry(client=client, checkpoint_latest=date(2026, 1, 5))

    result = registry.execute_for_source(
        source_key=FRED_FEDFUNDS_SOURCE_KEY,
        run_id="run-fred-incremental",
        trigger_type="scheduled",
        run_context={"api_key": "test-key"},
    )

    assert result.status == "success"
    assert len(client.calls) == 1
    assert client.calls[0]["series_id"] == FRED_FEDFUNDS_SERIES_ID
    assert client.calls[0]["start_date"] == date(2026, 1, 6)


def test_fred_source_reports_provider_failures() -> None:
    """Provider failures should produce deterministic failure outcome metadata."""
    client = _FakeClient(should_fail=True)
    registry, _capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=FRED_FEDFUNDS_SOURCE_KEY,
        run_id="run-fred-provider-fail",
        trigger_type="on_demand",
        run_context={"api_key": "test-key"},
    )

    assert result.status == "failure"
    assert result.failed_count == 1
    assert result.outcome_reason_code == "provider_request_failed"
