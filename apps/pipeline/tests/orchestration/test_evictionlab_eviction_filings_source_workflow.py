"""Contract tests for Eviction Lab eviction filings source workflow behavior."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any, Protocol, cast

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.services.canonical_ingest_service import CanonicalIngestService
from src.orchestration.jobs.source_ingest_runner import SourceIngestRunner
from src.orchestration.jobs.workflow_registry import SourceWorkflowRegistry
from src.sources.evictionlab_eviction_filings_source import (
    EVICTIONLAB_EVICTION_FILINGS_SOURCE_KEY,
    EVICTIONLAB_PROVIDER_GROUP_KEY,
    EVICTIONLAB_SOURCE_DESCRIPTION,
    EVICTIONLAB_SOURCE_NAME,
    EVICTIONLAB_SOURCE_TITLE,
    SERIES_CONFIGS,
    _aggregate_site_monthly,
    _DefaultEvictionLabClient,
    _map_records,
    _parse_month_to_iso,
    build_evictionlab_eviction_filings_source_workflow,
)

TWO = 2
THREE = 3
FIFTY_ONE = 51

# Expected aggregated filing values for _make_csv_rows with 3 geoids (3 × 10, 3 × 5, 3 × 3)
_EXPECTED_FILINGS_SUM = 30.0
_EXPECTED_FILINGS_AVG_SUM = 15.0
_EXPECTED_FILINGS_AVG_PRE_SUM = 9.0

# Expected aggregated filing values for mixed-validity rows
_EXPECTED_FILINGS_SINGLE = 5.0
_EXPECTED_FILINGS_AVG_SINGLE = 3.0
_EXPECTED_FILINGS_AVG_PRE_SINGLE = 2.0

# Expected filing for single good row
_EXPECTED_FILINGS_TEN = 10.0


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


class _FakeEvictionLabClient:
    def __init__(
        self,
        rows_by_slug: dict[str, list[dict[str, str]]] | None = None,
        *,
        should_fail: bool = False,
        fail_slugs: set[str] | None = None,
    ) -> None:
        self._rows_by_slug = rows_by_slug or {}
        self._should_fail = should_fail
        self._fail_slugs = fail_slugs or set()
        self.calls: list[dict[str, Any]] = []

    def fetch_monthly_csv(
        self,
        *,
        slug: str,
    ) -> list[dict[str, str]]:
        self.calls.append({"slug": slug})
        if self._should_fail or slug in self._fail_slugs:
            raise RuntimeError(f"evictionlab unavailable for {slug}")
        return self._rows_by_slug.get(slug, [])


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        del exc_type, exc, tb
        return False


class _FakeOpener:
    def __init__(self, payloads: list[bytes]) -> None:
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
    client: _FakeEvictionLabClient,
    checkpoint_latest_by_series: dict[str, date] | None = None,
) -> tuple[SourceWorkflowRegistry, _CaptureRepository]:
    capture_repo = _CaptureRepository()
    service = CanonicalIngestService(repository=capture_repo)
    runner = SourceIngestRunner(canonical_ingest_service=service)
    registry = SourceWorkflowRegistry()
    registry.register(
        build_evictionlab_eviction_filings_source_workflow(
            runner,
            observation_repository=_CheckpointRepo(checkpoint_latest_by_series),
            client=client,
        )
    )
    return registry, capture_repo


def _make_csv_rows(
    *,
    geoids: list[str],
    months: list[str],
    filings_2020: str = "10",
    filing_defaults: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    """Build synthetic CSV rows for testing."""
    defaults = {
        "filings_avg": "8",
        "filings_avg_prepandemic_baseline": "7",
        "last_updated": "2026-03-07",
    }
    if filing_defaults:
        defaults.update(filing_defaults)
    rows: list[dict[str, str]] = []
    for geoid in geoids:
        for month in months:
            rows.append(
                {
                    "type": "Census Tract",
                    "GEOID": geoid,
                    "racial_majority": "Unknown",
                    "month": month,
                    "filings_2020": filings_2020,
                    "filings_avg": defaults["filings_avg"],
                    "filings_avg_prepandemic_baseline": (
                        defaults["filings_avg_prepandemic_baseline"]
                    ),
                    "last_updated": defaults["last_updated"],
                }
            )
    return rows


# ---------------------------------------------------------------------------
# Series config generation
# ---------------------------------------------------------------------------


def test_series_configs_generates_fifty_one_entries() -> None:
    """SERIES_CONFIGS should contain exactly 51 site series."""
    assert len(SERIES_CONFIGS) == FIFTY_ONE
    assert all("canonical_series_key" in config for config in SERIES_CONFIGS)
    assert all(
        config["canonical_series_key"].startswith("HOUSING.US.EVICTION_FILINGS.")
        for config in SERIES_CONFIGS
    )


# ---------------------------------------------------------------------------
# _parse_month_to_iso
# ---------------------------------------------------------------------------


def test_parse_month_to_iso_valid_date() -> None:
    assert _parse_month_to_iso("01/2026") == "2026-01-01"
    assert _parse_month_to_iso("12/2024") == "2024-12-01"


def test_parse_month_to_iso_invalid_formats() -> None:
    assert _parse_month_to_iso("") is None
    assert _parse_month_to_iso("2026-01-01") is None
    assert _parse_month_to_iso("13/2026") is None
    assert _parse_month_to_iso("00/2026") is None
    assert _parse_month_to_iso("01/1999") is None
    assert _parse_month_to_iso("abc/def") is None


def test_parse_month_to_iso_strips_whitespace() -> None:
    assert _parse_month_to_iso("  03/2025  ") == "2025-03-01"


# ---------------------------------------------------------------------------
# _aggregate_site_monthly
# ---------------------------------------------------------------------------


def test_aggregate_site_monthly_sums_geoids() -> None:
    """Multiple GEOIDs in the same month should be summed."""
    rows = _make_csv_rows(
        geoids=["A", "B", "C"],
        months=["03/2026"],
        filings_2020="10",
        filing_defaults={"filings_avg": "5", "filings_avg_prepandemic_baseline": "3"},
    )
    result = _aggregate_site_monthly(rows, start_date=None)
    assert len(result) == 1
    assert result[0]["date"] == "2026-03-01"
    assert result[0]["filings"] == _EXPECTED_FILINGS_SUM
    assert result[0]["filings_avg"] == _EXPECTED_FILINGS_AVG_SUM
    assert result[0]["filings_avg_prepandemic"] == _EXPECTED_FILINGS_AVG_PRE_SUM


def test_aggregate_site_monthly_filters_by_start_date() -> None:
    """Rows with months before start_date should be excluded."""
    rows = _make_csv_rows(
        geoids=["A"],
        months=["01/2026", "02/2026", "03/2026"],
        filings_2020="10",
    )
    result = _aggregate_site_monthly(rows, start_date=date(2026, 2, 1))
    assert len(result) == TWO
    assert result[0]["date"] == "2026-02-01"
    assert result[1]["date"] == "2026-03-01"


def test_aggregate_site_monthly_skips_zero_filing_months() -> None:
    """Months with zero total filings should be dropped."""
    rows = _make_csv_rows(
        geoids=["A"],
        months=["03/2026"],
        filings_2020="0",
    )
    result = _aggregate_site_monthly(rows, start_date=None)
    assert result == []


def test_aggregate_site_monthly_handles_bad_values() -> None:
    """Non-numeric filing values should default to 0.0."""
    rows = [
        {
            "month": "03/2026",
            "GEOID": "A",
            "filings_2020": "bad",
            "filings_avg": "",
            "filings_avg_prepandemic_baseline": "notanumber",
            "last_updated": "2026-03-07",
        },
        {
            "month": "03/2026",
            "GEOID": "B",
            "filings_2020": "5",
            "filings_avg": "3",
            "filings_avg_prepandemic_baseline": "2",
            "last_updated": "2026-03-08",
        },
    ]
    result = _aggregate_site_monthly(rows, start_date=None)
    assert len(result) == 1
    assert result[0]["filings"] == _EXPECTED_FILINGS_SINGLE
    assert result[0]["filings_avg"] == _EXPECTED_FILINGS_AVG_SINGLE
    assert result[0]["filings_avg_prepandemic"] == _EXPECTED_FILINGS_AVG_PRE_SINGLE
    assert result[0]["last_updated"] == "2026-03-08"


def test_aggregate_site_monthly_handles_bad_avg_values() -> None:
    """Non-numeric filings_avg / filings_avg_prepandemic_baseline should default to 0.0."""
    rows = [
        {
            "month": "03/2026",
            "GEOID": "A",
            "filings_2020": "10",
            "filings_avg": "bad_avg",
            "filings_avg_prepandemic_baseline": "bad_pre",
            "last_updated": "2026-03-07",
        },
    ]
    result = _aggregate_site_monthly(rows, start_date=None)
    assert len(result) == 1
    assert result[0]["filings"] == _EXPECTED_FILINGS_TEN
    assert result[0]["filings_avg"] == 0.0
    assert result[0]["filings_avg_prepandemic"] == 0.0


def test_aggregate_site_monthly_skips_invalid_months() -> None:
    """Rows with unparsable month values should be silently skipped."""
    rows = [
        {
            "month": "invalid",
            "GEOID": "A",
            "filings_2020": "5",
            "filings_avg": "3",
            "filings_avg_prepandemic_baseline": "2",
            "last_updated": "2026-03-07",
        },
    ]
    result = _aggregate_site_monthly(rows, start_date=None)
    assert result == []


def test_aggregate_site_monthly_last_updated_takes_max() -> None:
    """last_updated should be the maximum across rows in the same month."""
    rows = [
        {
            "month": "03/2026",
            "GEOID": "A",
            "filings_2020": "5",
            "filings_avg": "3",
            "filings_avg_prepandemic_baseline": "2",
            "last_updated": "2026-03-01",
        },
        {
            "month": "03/2026",
            "GEOID": "B",
            "filings_2020": "5",
            "filings_avg": "3",
            "filings_avg_prepandemic_baseline": "2",
            "last_updated": "2026-03-15",
        },
    ]
    result = _aggregate_site_monthly(rows, start_date=None)
    assert result[0]["last_updated"] == "2026-03-15"


# ---------------------------------------------------------------------------
# _map_records
# ---------------------------------------------------------------------------


def test_map_records_produces_correct_canonical_fields() -> None:
    """Mapped records should contain all required canonical observation fields."""
    config = SERIES_CONFIGS[0]
    aggregated = [
        {
            "date": "2026-03-01",
            "filings": 150.0,
            "filings_avg": 120.0,
            "filings_avg_prepandemic": 110.0,
            "last_updated": "2026-03-07",
        }
    ]
    records = _map_records(aggregated_rows=aggregated, series_config=config)
    assert len(records) == 1
    record = records[0]
    assert record["source_name"] == EVICTIONLAB_SOURCE_NAME
    assert record["source_key"] == EVICTIONLAB_PROVIDER_GROUP_KEY
    assert record["source_title"] == EVICTIONLAB_SOURCE_TITLE
    assert record["source_description"] == EVICTIONLAB_SOURCE_DESCRIPTION
    assert record["source_type"] == "external"
    assert record["series_key"] == config["canonical_series_key"]
    assert record["metric_name"] == config["metric_name"]
    assert record["date"] == "2026-03-01"
    assert record["reported_at"] == "2026-03-07T00:00:00+00:00"
    assert record["value"] == "150"
    assert record["unit"] == "filings"
    assert record["unit_type"] == "number"
    attributes = record["attributes"]
    assert isinstance(attributes, dict)
    attributes_payload = cast(dict[str, object], attributes)
    assert attributes_payload["provider_series_id"] == config["provider_series_id"]
    assert attributes_payload["filings_avg"] == "120.0"
    assert attributes_payload["filings_avg_prepandemic"] == "110.0"


def test_map_records_formats_fractional_values() -> None:
    """Non-integer filing totals should be formatted as floats."""
    config = SERIES_CONFIGS[0]
    aggregated = [
        {
            "date": "2026-03-01",
            "filings": 150.5,
            "filings_avg": 0,
            "filings_avg_prepandemic": 0,
            "last_updated": "",
        }
    ]
    records = _map_records(aggregated_rows=aggregated, series_config=config)
    assert records[0]["value"] == "150.5"


def test_map_records_skips_rows_with_missing_required_fields() -> None:
    """Rows missing date or filings should be dropped."""
    config = SERIES_CONFIGS[0]
    aggregated: list[dict[str, Any]] = [
        {"date": None, "filings": 10.0},
        {"date": "2026-03-01", "filings": None},
    ]
    records = _map_records(aggregated_rows=aggregated, series_config=config)
    assert records == []


# ---------------------------------------------------------------------------
# _DefaultEvictionLabClient
# ---------------------------------------------------------------------------


def test_default_evictionlab_client_fetches_and_parses_csv() -> None:
    """The default client should download CSV bytes and parse them into dicts."""
    csv_content = (
        "type,GEOID,racial_majority,month,filings_2020,filings_avg,"
        "filings_avg_prepandemic_baseline,last_updated\n"
        "Census Tract,12345,,03/2026,10,8,7,2026-03-07\n"
        "Census Tract,67890,,03/2026,5,4,3,2026-03-07\n"
    )
    client = _DefaultEvictionLabClient(
        base_url_template="https://example.test/{slug}_monthly_2020_2021.csv",
        timeout=15,
    )
    opener = _FakeOpener([csv_content.encode("utf-8")])
    client._opener = cast(Any, opener)  # pyright: ignore[reportPrivateUsage]

    rows = client.fetch_monthly_csv(slug="albuquerque")

    assert len(rows) == TWO
    assert rows[0]["filings_2020"] == "10"
    assert rows[1]["GEOID"] == "67890"
    assert opener.calls == [("https://example.test/albuquerque_monthly_2020_2021.csv", 15)]


# ---------------------------------------------------------------------------
# Workflow: passthrough
# ---------------------------------------------------------------------------


def test_evictionlab_source_rejects_non_list_passthrough_records() -> None:
    """Passthrough with non-list records should raise ValueError."""
    client = _FakeEvictionLabClient(rows_by_slug={})
    registry, _capture_repo = _build_registry(client=client)

    with pytest.raises(ValueError, match="run_context.records must be a list"):
        registry.execute_for_source(
            source_key=EVICTIONLAB_EVICTION_FILINGS_SOURCE_KEY,
            run_id="run-evictionlab-bad-passthrough",
            trigger_type="on_demand",
            run_context={"records": "not-a-list"},
        )


def test_evictionlab_source_supports_passthrough_records() -> None:
    """Passthrough mode should validate and ingest canonical records."""
    client = _FakeEvictionLabClient(rows_by_slug={})
    registry, capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=EVICTIONLAB_EVICTION_FILINGS_SOURCE_KEY,
        run_id="run-evictionlab-passthrough",
        trigger_type="on_demand",
        run_context={
            "records": [
                {
                    "source_name": EVICTIONLAB_SOURCE_NAME,
                    "source_key": EVICTIONLAB_PROVIDER_GROUP_KEY,
                    "source_title": EVICTIONLAB_SOURCE_TITLE,
                    "source_description": EVICTIONLAB_SOURCE_DESCRIPTION,
                    "source_type": "external",
                    "series_key": "HOUSING.US.EVICTION_FILINGS.TEST",
                    "metric_name": "Test",
                    "dataset_title": "Test",
                    "date": "2026-01-01",
                    "reported_at": "2026-01-02T00:00:00Z",
                    "value": "100",
                    "attributes": {},
                }
            ]
        },
    )

    assert result.accepted_count == 1
    assert len(capture_repo.rows) == 1


# ---------------------------------------------------------------------------
# Workflow: fetch → aggregate → map → ingest (happy path)
# ---------------------------------------------------------------------------


def test_evictionlab_source_maps_series_and_uses_incremental_start_dates() -> None:
    """Handler should fetch CSV, aggregate, and ingest records with per-series checkpoints."""
    first = SERIES_CONFIGS[0]
    second = SERIES_CONFIGS[1]

    rows_first = _make_csv_rows(
        geoids=["A", "B"],
        months=["01/2026", "02/2026"],
        filings_2020="10",
        filing_defaults={
            "filings_avg": "8",
            "filings_avg_prepandemic_baseline": "7",
            "last_updated": "2026-03-07",
        },
    )
    rows_second = _make_csv_rows(
        geoids=["C"],
        months=["03/2026"],
        filings_2020="20",
        filing_defaults={
            "filings_avg": "15",
            "filings_avg_prepandemic_baseline": "12",
            "last_updated": "2026-03-10",
        },
    )

    client = _FakeEvictionLabClient(
        rows_by_slug={
            first["csv_slug"]: rows_first,
            second["csv_slug"]: rows_second,
        }
    )
    registry, capture_repo = _build_registry(
        client=client,
        checkpoint_latest_by_series={
            first["canonical_series_key"]: date(2026, 1, 15),
            second["canonical_series_key"]: date(2026, 2, 1),
        },
    )

    result = registry.execute_for_source(
        source_key=EVICTIONLAB_EVICTION_FILINGS_SOURCE_KEY,
        run_id="run-evictionlab-success",
        trigger_type="scheduled",
        run_context={
            "series_item_keys": [first["series_item_key"], second["series_item_key"]],
        },
    )

    assert result.status == "success"
    # first series: start_date = 2026-01-16 -> only 02/2026 passes (20 filings from 2 GEOIDs)
    # second series: start_date = 2026-02-02 -> only 03/2026 passes (20 filings from 1 GEOID)
    assert result.accepted_count == TWO
    assert len(capture_repo.rows) == TWO
    assert result.cadence_decisions == []
    assert all("cadence_decision" in outcome for outcome in result.series_outcomes)
    assert len(result.series_outcomes) == TWO

    # Verify start_date filtering was applied correctly
    assert len(client.calls) == TWO
    assert {str(row.source_key) for row in capture_repo.rows} == {EVICTIONLAB_PROVIDER_GROUP_KEY}
    assert {str(row.source_title) for row in capture_repo.rows} == {EVICTIONLAB_SOURCE_TITLE}
    assert {str(row.unit_type) for row in capture_repo.rows} == {"number"}


# ---------------------------------------------------------------------------
# Workflow: series_item_keys filtering
# ---------------------------------------------------------------------------


def test_evictionlab_source_filters_by_series_item_keys() -> None:
    """When series_item_keys is provided, only those series should be fetched."""
    first = SERIES_CONFIGS[0]

    client = _FakeEvictionLabClient(
        rows_by_slug={
            first["csv_slug"]: _make_csv_rows(
                geoids=["A"],
                months=["03/2026"],
                filings_2020="10",
            ),
        }
    )
    registry, _capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=EVICTIONLAB_EVICTION_FILINGS_SOURCE_KEY,
        run_id="run-evictionlab-filter",
        trigger_type="on_demand",
        run_context={
            "series_item_keys": [first["series_item_key"]],
        },
    )

    assert result.status == "success"
    assert result.accepted_count == 1
    assert len(client.calls) == 1
    assert client.calls[0]["slug"] == first["csv_slug"]
    assert len(result.series_outcomes) == 1


# ---------------------------------------------------------------------------
# Workflow: partial failure
# ---------------------------------------------------------------------------


def test_evictionlab_source_reports_partial_failure_for_series_errors() -> None:
    """Mixed fetch results should return partial_success with per-series failures."""
    first = SERIES_CONFIGS[0]
    second = SERIES_CONFIGS[1]

    client = _FakeEvictionLabClient(
        rows_by_slug={
            first["csv_slug"]: _make_csv_rows(
                geoids=["A"],
                months=["03/2026"],
                filings_2020="10",
            ),
        },
        fail_slugs={second["csv_slug"]},
    )
    registry, _capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=EVICTIONLAB_EVICTION_FILINGS_SOURCE_KEY,
        run_id="run-evictionlab-partial",
        trigger_type="on_demand",
        run_context={
            "series_item_keys": [first["series_item_key"], second["series_item_key"]],
        },
    )

    assert result.status == "partial_success"
    assert result.accepted_count == 1
    assert result.failed_count == 1
    assert len(result.series_outcomes) == TWO

    failed_outcome = next(
        outcome
        for outcome in result.series_outcomes
        if outcome["provider_series_id"] == second["provider_series_id"]
    )
    assert failed_outcome["status"] == "failure"
    assert failed_outcome["outcome_reason_code"] == "provider_request_failed"


# ---------------------------------------------------------------------------
# Workflow: all series fail
# ---------------------------------------------------------------------------


def test_evictionlab_source_reports_failure_when_all_series_fail() -> None:
    """When all configured series fail provider retrieval, workflow should fail."""
    first = SERIES_CONFIGS[0]
    second = SERIES_CONFIGS[1]

    client = _FakeEvictionLabClient(should_fail=True)
    registry, _capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=EVICTIONLAB_EVICTION_FILINGS_SOURCE_KEY,
        run_id="run-evictionlab-failure",
        trigger_type="on_demand",
        run_context={
            "series_item_keys": [first["series_item_key"], second["series_item_key"]],
        },
    )

    assert result.status == "failure"
    assert result.failed_count == TWO
    assert result.accepted_count == 0
    assert result.outcome_reason_code == "provider_request_failed"
    assert len(result.series_outcomes) == TWO
