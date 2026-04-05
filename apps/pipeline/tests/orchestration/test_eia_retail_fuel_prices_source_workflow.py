"""Contract tests for EIA retail fuel prices source workflow behavior."""

# ruff: noqa: D103

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Protocol, cast

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.services.canonical_ingest_service import CanonicalIngestService
from src.orchestration.jobs.source_ingest_runner import SourceIngestRunner
from src.orchestration.jobs.workflow_registry import SourceWorkflowRegistry
from src.sources.eia_retail_fuel_prices_source import (
    EIA_PROVIDER_GROUP_KEY,
    EIA_RETAIL_FUEL_PRICES_SOURCE_KEY,
    EIA_SOURCE_DESCRIPTION,
    EIA_SOURCE_TITLE,
    SERIES_CONFIGS,
    _DefaultEiaClient,
    build_eia_retail_fuel_prices_source_workflow,
)

TWO = 2


class _Observation(Protocol):
    source_key: object
    source_title: object
    source_description: object
    series_key: object
    observed_on: object
    unit_type: object


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


class _FakeEiaClient:
    def __init__(
        self,
        rows_by_key: dict[tuple[str, str], list[dict[str, Any]]] | None = None,
        *,
        should_fail: bool = False,
        fail_keys: set[tuple[str, str]] | None = None,
    ) -> None:
        self._rows_by_key = rows_by_key or {}
        self._should_fail = should_fail
        self._fail_keys = fail_keys or set()
        self.calls: list[dict[str, Any]] = []

    def fetch_observations(
        self,
        *,
        api_key: str,
        product_code: str,
        duoarea: str,
        start_date: date | None,
    ) -> list[dict[str, Any]]:
        self.calls.append(
            {
                "api_key": api_key,
                "product_code": product_code,
                "duoarea": duoarea,
                "start_date": start_date,
            }
        )
        key = (product_code, duoarea)
        if self._should_fail or key in self._fail_keys:
            raise RuntimeError("eia unavailable")
        return self._rows_by_key.get(key, [])


class _FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        del exc_type, exc, tb
        return False


class _FakeOpener:
    def __init__(self, payloads: list[dict[str, object]]) -> None:
        self._payloads = payloads
        self.calls: list[tuple[str, int]] = []

    def open(self, url: str, timeout: int):
        self.calls.append((url, timeout))
        index = len(self.calls) - 1
        if index >= len(self._payloads):
            raise RuntimeError("unexpected open call")
        return _FakeResponse(self._payloads[index])


def _build_registry(
    *,
    client: _FakeEiaClient,
    checkpoint_latest_by_series: dict[str, date] | None = None,
) -> tuple[SourceWorkflowRegistry, _CaptureRepository]:
    capture_repo = _CaptureRepository()
    service = CanonicalIngestService(repository=capture_repo)
    runner = SourceIngestRunner(canonical_ingest_service=service)
    registry = SourceWorkflowRegistry()
    registry.register(
        build_eia_retail_fuel_prices_source_workflow(
            runner,
            observation_repository=_CheckpointRepo(checkpoint_latest_by_series),
            client=client,
        )
    )
    return registry, capture_repo


def test_default_eia_client_handles_pagination_and_start_date() -> None:
    client = _DefaultEiaClient(base_url="https://example.test", timeout=12, page_size=2)
    opener = _FakeOpener(
        [
            {
                "response": {
                    "data": [
                        {"period": "2026-01-01", "value": "3.00"},
                        "invalid",
                    ],
                    "total": TWO,
                }
            },
            {
                "response": {
                    "data": [
                        {"period": "2026-01-08", "value": "3.10"},
                    ],
                    "total": TWO,
                }
            },
        ]
    )
    client._opener = cast(Any, opener)  # pyright: ignore[reportPrivateUsage]

    rows = client.fetch_observations(
        api_key="test-key",
        product_code="EPMR",
        duoarea="NUS",
        start_date=date(2026, 1, 1),
    )

    assert len(rows) == TWO
    assert "start=2026-01-01" in opener.calls[0][0]
    assert "offset=2" in opener.calls[1][0]


def test_default_eia_client_rejects_invalid_response_shapes() -> None:
    client = _DefaultEiaClient(base_url="https://example.test", page_size=1)
    opener = _FakeOpener([{"response": {"data": "bad"}}])
    client._opener = cast(Any, opener)  # pyright: ignore[reportPrivateUsage]

    with pytest.raises(RuntimeError, match="eia response data payload is invalid"):
        client.fetch_observations(
            api_key="k",
            product_code="EPMR",
            duoarea="NUS",
            start_date=None,
        )


def test_eia_source_requires_credentials() -> None:
    client = _FakeEiaClient(rows_by_key={})
    registry, _capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=EIA_RETAIL_FUEL_PRICES_SOURCE_KEY,
        run_id="run-eia-missing-key",
        trigger_type="on_demand",
        run_context={},
    )

    assert result.status == "failure"
    assert result.outcome_reason_code == "missing_credentials"
    assert len(client.calls) == 0


def test_eia_source_supports_passthrough_records() -> None:
    client = _FakeEiaClient(rows_by_key={})
    registry, capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=EIA_RETAIL_FUEL_PRICES_SOURCE_KEY,
        run_id="run-eia-passthrough",
        trigger_type="on_demand",
        run_context={
            "records": [
                {
                    "source_name": "EIA",
                    "source_key": EIA_PROVIDER_GROUP_KEY,
                    "source_title": EIA_SOURCE_TITLE,
                    "source_description": EIA_SOURCE_DESCRIPTION,
                    "source_type": "external",
                    "series_key": "ENERGY.US.TEST",
                    "metric_name": "Test",
                    "dataset_title": "Test",
                    "date": "2026-01-01",
                    "reported_at": "2026-01-02T00:00:00Z",
                    "value": "1.0",
                    "attributes": {},
                }
            ]
        },
    )

    assert result.accepted_count == 1
    assert len(capture_repo.rows) == 1


def test_eia_source_maps_series_and_uses_incremental_start_dates() -> None:
    first = SERIES_CONFIGS[0]
    second = SERIES_CONFIGS[1]
    client = _FakeEiaClient(
        rows_by_key={
            (first["provider_product_code"], first["provider_duoarea"]): [
                {
                    "period": "2026-01-08",
                    "value": "3.21",
                    "updated": "2026-01-09T00:00:00Z",
                    "units": "Dollars per Gallon",
                }
            ],
            (second["provider_product_code"], second["provider_duoarea"]): [
                {
                    "period": "2026-01-08",
                    "value": "3.31",
                    "last-updated": "2026-01-09T00:00:00Z",
                }
            ],
        }
    )

    registry, capture_repo = _build_registry(
        client=client,
        checkpoint_latest_by_series={
            first["canonical_series_key"]: date(2026, 1, 1),
            second["canonical_series_key"]: date(2026, 1, 2),
        },
    )

    result = registry.execute_for_source(
        source_key=EIA_RETAIL_FUEL_PRICES_SOURCE_KEY,
        run_id="run-eia-success",
        trigger_type="scheduled",
        run_context={
            "api_key": "test-key",
            "series_item_keys": [first["series_item_key"], second["series_item_key"]],
        },
    )

    assert result.status == "success"
    assert result.accepted_count == TWO
    assert len(capture_repo.rows) == TWO
    assert len(client.calls) == TWO
    assert result.cadence_decisions == []
    assert all("cadence_decision" in outcome for outcome in result.series_outcomes)
    call_map = {(call["product_code"], call["duoarea"]): call for call in client.calls}
    assert call_map[(first["provider_product_code"], first["provider_duoarea"])][
        "start_date"
    ] == date(2026, 1, 2)
    assert call_map[(second["provider_product_code"], second["provider_duoarea"])][
        "start_date"
    ] == date(2026, 1, 3)
    assert {str(row.unit_type) for row in capture_repo.rows} == {"usd"}
    assert {str(row.source_key) for row in capture_repo.rows} == {EIA_PROVIDER_GROUP_KEY}
    assert {str(row.source_title) for row in capture_repo.rows} == {EIA_SOURCE_TITLE}


def test_eia_source_reports_partial_failure_for_series_errors() -> None:
    first = SERIES_CONFIGS[0]
    second = SERIES_CONFIGS[1]
    client = _FakeEiaClient(
        rows_by_key={
            (first["provider_product_code"], first["provider_duoarea"]): [
                {"period": "2026-01-08", "value": "3.21"}
            ]
        },
        fail_keys={(second["provider_product_code"], second["provider_duoarea"])},
    )
    registry, _capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=EIA_RETAIL_FUEL_PRICES_SOURCE_KEY,
        run_id="run-eia-partial",
        trigger_type="on_demand",
        run_context={
            "api_key": "test-key",
            "series_item_keys": [first["series_item_key"], second["series_item_key"]],
        },
    )

    assert result.status == "partial_success"
    assert result.failed_count == 1
    assert result.accepted_count == 1


def test_eia_source_reports_failure_when_all_series_fail() -> None:
    first = SERIES_CONFIGS[0]
    second = SERIES_CONFIGS[1]
    client = _FakeEiaClient(should_fail=True)
    registry, _capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=EIA_RETAIL_FUEL_PRICES_SOURCE_KEY,
        run_id="run-eia-failure",
        trigger_type="on_demand",
        run_context={
            "api_key": "test-key",
            "series_item_keys": [first["series_item_key"], second["series_item_key"]],
        },
    )

    assert result.status == "failure"
    assert result.failed_count == TWO
    assert result.accepted_count == 0
    assert result.outcome_reason_code == "provider_request_failed"
