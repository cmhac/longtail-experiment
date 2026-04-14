"""Contract tests for JDI jail population source workflow behavior."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Protocol

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.services.canonical_ingest_service import CanonicalIngestService
from src.orchestration.jobs.source_ingest_runner import SourceIngestRunner
from src.orchestration.jobs.workflow_registry import SourceWorkflowRegistry
from src.sources.jdi_jail_population_source import (
    JDI_JAIL_POPULATION_SOURCE_KEY,
    JDI_PROVIDER_GROUP_KEY,
    JDI_SOURCE_DESCRIPTION,
    JDI_SOURCE_NAME,
    JDI_SOURCE_TITLE,
    JDI_TOTAL_CANONICAL_SERIES_KEY,
    JDI_TOTAL_SERIES_ITEM_KEY,
    JDI_WHITELISTED_SERIES_ITEM_KEYS,
    _build_records,
    _map_jdi_records,
    _roster_series_key,
    build_jdi_jail_population_source_workflow,
)

INPUT_ROW_COUNT = 1200
EXPECTED_DAILY_DATES = 28


class _Observation(Protocol):
    source_key: object
    source_title: object
    source_description: object
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


class _FakeJdiClient:
    def __init__(
        self, rows: list[dict[str, str]] | None = None, *, should_fail: bool = False
    ) -> None:
        self._rows = rows or []
        self._should_fail = should_fail
        self.calls = 0

    def fetch_observations(self) -> list[dict[str, str]]:
        self.calls += 1
        if self._should_fail:
            raise RuntimeError("jdi unavailable")
        return self._rows


def _build_registry(
    *,
    client: _FakeJdiClient,
    checkpoint_latest_by_series: dict[str, date] | None = None,
) -> tuple[SourceWorkflowRegistry, _CaptureRepository]:
    capture_repo = _CaptureRepository()
    service = CanonicalIngestService(repository=capture_repo)
    runner = SourceIngestRunner(canonical_ingest_service=service)
    registry = SourceWorkflowRegistry()
    registry.register(
        build_jdi_jail_population_source_workflow(
            runner,
            observation_repository=_CheckpointRepo(checkpoint_latest_by_series),
            client=client,
        )
    )
    return registry, capture_repo


def _rows_for_range(*, start: int = 1, end: int = 1200) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for i in range(start, end + 1):
        roster_id = "AL-Butler" if i % 2 else "TX-Harris"
        state = "AL" if i % 2 else "TX"
        day = ((i - 1) % 28) + 1
        rows.append(
            {
                "State": state,
                "Roster_ID": roster_id,
                "Date": f"2026-03-{day:02d}",
                "Population_Interpolated": str(100 + i),
                "As_Of": "2026-04-02 03:32:55",
            }
        )
    return rows


def test_roster_series_key_uses_state_and_roster_id_tokens() -> None:
    key = _roster_series_key(state="AL", roster_id="AL-Butler")
    assert key == "JUSTICE.US.JAIL_POPULATION.AL.AL_BUTLER"


def test_build_records_maps_jail_and_total_series() -> None:
    rows = _rows_for_range(end=1200)
    records, dynamic_series_count = _build_records(
        rows=rows,
        observation_repository=_CheckpointRepo(),
        requested_series_items=None,
    )
    assert records
    assert dynamic_series_count > 0
    assert any(record["series_key"] == JDI_TOTAL_CANONICAL_SERIES_KEY for record in records)
    assert any(
        str(record["series_key"]).startswith("JUSTICE.US.JAIL_POPULATION.TX.") for record in records
    )
    assert not any(
        str(record["series_key"]).startswith("JUSTICE.US.JAIL_POPULATION.AL.") for record in records
    )


def test_build_records_enforces_parse_success_guardrail() -> None:
    rows = _rows_for_range(end=1200)
    rows[0]["Population_Interpolated"] = "not-a-number"
    rows[1]["Date"] = "bad-date"
    rows[2]["Roster_ID"] = ""
    rows[3]["State"] = ""
    rows[4]["Population_Interpolated"] = ""
    rows[5]["Date"] = ""
    rows[6]["Population_Interpolated"] = "nan!"
    rows[7]["Date"] = "2026/03/02"
    rows[8]["State"] = ""
    rows[9]["Roster_ID"] = ""
    rows[10]["Population_Interpolated"] = ""
    rows[11]["Date"] = ""
    rows[12]["Population_Interpolated"] = "bad"

    with pytest.raises(RuntimeError, match="parse-success"):
        _build_records(
            rows=rows,
            observation_repository=_CheckpointRepo(),
            requested_series_items=None,
        )


def test_build_records_enforces_row_count_guardrail() -> None:
    rows = _rows_for_range(end=50)
    with pytest.raises(RuntimeError, match="row-count sanity check"):
        _build_records(
            rows=rows,
            observation_repository=_CheckpointRepo(),
            requested_series_items=None,
        )


def test_map_jdi_records_is_alias_for_required_mapper_name() -> None:
    rows = _rows_for_range(end=1200)
    mapped, dynamic_series_count = _map_jdi_records(
        rows=rows,
        observation_repository=_CheckpointRepo(),
        requested_series_items=None,
    )
    assert mapped
    assert dynamic_series_count > 0


def test_jdi_source_supports_passthrough_records() -> None:
    client = _FakeJdiClient(rows=[])
    registry, capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=JDI_JAIL_POPULATION_SOURCE_KEY,
        run_id="run-jdi-passthrough",
        trigger_type="on_demand",
        run_context={
            "records": [
                {
                    "source_name": JDI_SOURCE_NAME,
                    "source_key": JDI_PROVIDER_GROUP_KEY,
                    "source_title": JDI_SOURCE_TITLE,
                    "source_description": JDI_SOURCE_DESCRIPTION,
                    "source_type": "external",
                    "series_key": "JUSTICE.US.JAIL_POPULATION.TEST.X",
                    "metric_name": "Test",
                    "dataset_title": "Test",
                    "date": "2026-03-01",
                    "reported_at": "2026-03-02T00:00:00Z",
                    "value": "123",
                    "attributes": {},
                }
            ]
        },
    )

    assert result.status == "success"
    assert result.accepted_count == 1
    assert len(capture_repo.rows) == 1


def test_jdi_source_filters_out_non_total_series_requests() -> None:
    client = _FakeJdiClient(rows=_rows_for_range(end=1200))
    registry, capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=JDI_JAIL_POPULATION_SOURCE_KEY,
        run_id="run-jdi-filtered",
        trigger_type="on_demand",
        run_context={"series_item_keys": ["some_other_series"]},
    )

    assert result.status == "success"
    assert result.accepted_count == 0
    assert client.calls == 0
    assert len(capture_repo.rows) == 0


def test_jdi_source_ingests_jail_and_total_records() -> None:
    rows = _rows_for_range(end=INPUT_ROW_COUNT)
    client = _FakeJdiClient(rows=rows)
    registry, capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=JDI_JAIL_POPULATION_SOURCE_KEY,
        run_id="run-jdi-success",
        trigger_type="scheduled",
        run_context={"series_item_keys": [JDI_TOTAL_SERIES_ITEM_KEY]},
    )

    assert result.status == "success"
    assert result.accepted_count > 0
    assert result.accepted_count < INPUT_ROW_COUNT
    assert client.calls == 1
    assert len(capture_repo.rows) == result.accepted_count
    assert any(str(row.series_key) == JDI_TOTAL_CANONICAL_SERIES_KEY for row in capture_repo.rows)
    assert not any(
        str(row.series_key).startswith("JUSTICE.US.JAIL_POPULATION.AL.")
        for row in capture_repo.rows
    )


def test_jdi_source_total_series_aggregates_non_whitelist_rows() -> None:
    rows = [
        {
            "State": "AL",
            "Roster_ID": "AL-Butler",
            "Date": f"2026-03-{((i - 1) % 28) + 1:02d}",
            "Population_Interpolated": "10",
            "As_Of": "2026-04-02 03:32:55",
        }
        for i in range(1, INPUT_ROW_COUNT + 1)
    ]
    client = _FakeJdiClient(rows=rows)
    registry, capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=JDI_JAIL_POPULATION_SOURCE_KEY,
        run_id="run-jdi-total-only",
        trigger_type="scheduled",
        run_context={"series_item_keys": [JDI_TOTAL_SERIES_ITEM_KEY]},
    )

    assert result.status == "success"
    assert result.accepted_count == EXPECTED_DAILY_DATES
    assert len(capture_repo.rows) == EXPECTED_DAILY_DATES
    assert all(str(row.series_key) == JDI_TOTAL_CANONICAL_SERIES_KEY for row in capture_repo.rows)


def test_jdi_source_whitelist_series_request_omits_total() -> None:
    tx_harris_item_key = next(
        key for key in JDI_WHITELISTED_SERIES_ITEM_KEYS if key.endswith("tx_harris")
    )
    client = _FakeJdiClient(rows=_rows_for_range(end=INPUT_ROW_COUNT))
    registry, capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=JDI_JAIL_POPULATION_SOURCE_KEY,
        run_id="run-jdi-whitelist-only",
        trigger_type="scheduled",
        run_context={"series_item_keys": [tx_harris_item_key]},
    )

    assert result.status == "success"
    assert result.accepted_count > 0
    assert not any(
        str(row.series_key) == JDI_TOTAL_CANONICAL_SERIES_KEY for row in capture_repo.rows
    )


def test_jdi_source_reports_failure_when_provider_request_fails() -> None:
    client = _FakeJdiClient(should_fail=True)
    registry, _capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=JDI_JAIL_POPULATION_SOURCE_KEY,
        run_id="run-jdi-failure",
        trigger_type="on_demand",
        run_context={"series_item_keys": [JDI_TOTAL_SERIES_ITEM_KEY]},
    )

    assert result.status == "failure"
    assert result.failed_count == 1
    assert result.outcome_reason_code == "provider_request_failed"
