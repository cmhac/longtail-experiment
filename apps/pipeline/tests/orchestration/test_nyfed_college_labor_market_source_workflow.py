"""Contract tests for NY Fed college labor market source workflow behavior."""

from __future__ import annotations

import sys
import zipfile
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Any, Protocol

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.services.canonical_ingest_service import CanonicalIngestService
from src.orchestration.jobs.source_ingest_runner import SourceIngestRunner
from src.orchestration.jobs.workflow_registry import SourceWorkflowRegistry
from src.sources.nyfed_college_labor_market_source import (
    NYFED_COLLEGE_LABOR_MARKET_SOURCE_KEY,
    NYFED_PROVIDER_GROUP_KEY,
    NYFED_SOURCE_DESCRIPTION,
    NYFED_SOURCE_TITLE,
    SERIES_CONFIGS,
    _DefaultNyfedClient,
    _parse_workbook_bytes,
    build_nyfed_college_labor_market_source_workflow,
)

FOUR = 4
THREE = 3


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


class _FakeNyfedClient:
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
        provider_series_id: str,
        start_date: date | None,
    ) -> list[dict[str, Any]]:
        self.calls.append(
            {
                "provider_series_id": provider_series_id,
                "start_date": start_date,
            }
        )
        if self._should_fail or provider_series_id in self._fail_series_ids:
            raise RuntimeError("nyfed unavailable")
        return self._rows_by_series.get(provider_series_id, [])


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


def _inline_sheet_xml(rows: list[dict[str, str]]) -> str:
    xml_rows: list[str] = []
    for index, row in enumerate(rows, start=1):
        cells = "".join(
            f'<c r="{column}{index}" t="inlineStr"><is><t>{value}</t></is></c>'
            for column, value in row.items()
        )
        xml_rows.append(f'<row r="{index}">{cells}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{''.join(xml_rows)}</sheetData>"
        "</worksheet>"
    )


def _build_workbook_bytes(
    *,
    unemployed_rows: list[tuple[str, str, str]],
    underemployed_rows: list[tuple[str, str, str]],
    updated_label: str = "Updated: February 4, 2026",
) -> bytes:
    cover_rows = [{}, {"A": "placeholder"}]
    unemployed_sheet_rows: list[dict[str, str]] = [
        {},
        {},
        {},
        {},
        {},
        {},
        {"A": "Chart and Table Data"},
        {"A": updated_label},
        {"A": "Source"},
        {},
        {
            "A": "Date",
            "B": "Young workers",
            "C": "All workers",
            "D": "Recent graduates",
            "E": "College graduates",
        },
    ]
    unemployed_sheet_rows.extend(
        {"A": d, "B": "0.0", "C": "0.0", "D": recent, "E": college}
        for d, recent, college in unemployed_rows
    )
    underemployed_sheet_rows: list[dict[str, str]] = [
        {},
        {},
        {},
        {},
        {},
        {},
        {"A": "Chart and Table Data"},
        {"A": updated_label},
        {"A": "Source"},
        {},
        {
            "A": "Date",
            "B": "Recent graduates",
            "C": "College graduates",
        },
    ]
    underemployed_sheet_rows.extend(
        {"A": d, "B": recent, "C": college} for d, recent, college in underemployed_rows
    )

    workbook_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Cover Sheet" sheetId="1" r:id="rId1"/>
    <sheet name="unemployed" sheetId="2" r:id="rId2"/>
    <sheet name="underemployed" sheetId="3" r:id="rId3"/>
  </sheets>
</workbook>
"""
    rels_xml = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
            '  <Relationship Id="rId1"'
            ' Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"'
            ' Target="worksheets/sheet1.xml"/>',
            '  <Relationship Id="rId2"'
            ' Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"'
            ' Target="worksheets/sheet2.xml"/>',
            '  <Relationship Id="rId3"'
            ' Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"'
            ' Target="worksheets/sheet3.xml"/>',
            "</Relationships>",
            "",
        ]
    )
    content_types_xml = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
            '  <Default Extension="rels"'
            ' ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
            '  <Default Extension="xml" ContentType="application/xml"/>',
            '  <Override PartName="/xl/workbook.xml"'
            ' ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.sheet.main+xml"/>',
            '  <Override PartName="/xl/worksheets/sheet1.xml"'
            ' ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.worksheet+xml"/>',
            '  <Override PartName="/xl/worksheets/sheet2.xml"'
            ' ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.worksheet+xml"/>',
            '  <Override PartName="/xl/worksheets/sheet3.xml"'
            ' ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.worksheet+xml"/>',
            "</Types>",
            "",
        ]
    )
    package_rels_xml = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
            '  <Relationship Id="rId1"'
            ' Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"'
            ' Target="xl/workbook.xml"/>',
            "</Relationships>",
            "",
        ]
    )

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", content_types_xml)
        archive.writestr("_rels/.rels", package_rels_xml)
        archive.writestr("xl/workbook.xml", workbook_xml)
        archive.writestr("xl/_rels/workbook.xml.rels", rels_xml)
        archive.writestr("xl/worksheets/sheet1.xml", _inline_sheet_xml(cover_rows))
        archive.writestr("xl/worksheets/sheet2.xml", _inline_sheet_xml(unemployed_sheet_rows))
        archive.writestr("xl/worksheets/sheet3.xml", _inline_sheet_xml(underemployed_sheet_rows))
    return buffer.getvalue()


def _build_registry(
    *,
    client: _FakeNyfedClient,
    checkpoint_latest_by_series: dict[str, date] | None = None,
) -> tuple[SourceWorkflowRegistry, _CaptureRepository]:
    capture_repo = _CaptureRepository()
    service = CanonicalIngestService(repository=capture_repo)
    runner = SourceIngestRunner(canonical_ingest_service=service)
    registry = SourceWorkflowRegistry()
    registry.register(
        build_nyfed_college_labor_market_source_workflow(
            runner,
            observation_repository=_CheckpointRepo(checkpoint_latest_by_series),
            client=client,
        )
    )
    return registry, capture_repo


def test_parse_workbook_bytes_extracts_all_four_series() -> None:
    """Workbook parsing should emit all configured series with normalized dates."""
    workbook = _build_workbook_bytes(
        unemployed_rows=[("32874", "3.381", "2.27"), ("32905", "3.039", "2.206")],
        underemployed_rows=[("32874", "42.918", "34.081"), ("32905", "43.244", "34.085")],
    )

    parsed = _parse_workbook_bytes(workbook)

    assert set(parsed) == {config["provider_series_id"] for config in SERIES_CONFIGS}
    assert parsed["unemployed_recent_graduates"][0]["date"] == "1990-01-01"
    assert parsed["unemployed_college_graduates"][1]["value"] == "2.206"
    assert parsed["underemployed_recent_graduates"][0]["reported_at"] == "2026-02-04T00:00:00+00:00"


def test_parse_workbook_bytes_rejects_missing_required_value() -> None:
    """Blank target cells should fail parsing instead of silently dropping rows."""
    workbook = _build_workbook_bytes(
        unemployed_rows=[("32874", "3.381", "")],
        underemployed_rows=[("32874", "42.918", "34.081")],
    )

    with pytest.raises(RuntimeError, match="missing required value"):
        _parse_workbook_bytes(workbook)


def test_default_nyfed_client_filters_rows_by_start_date() -> None:
    """The default client should apply start-date filtering after workbook parsing."""
    workbook = _build_workbook_bytes(
        unemployed_rows=[("32874", "3.381", "2.27"), ("32905", "3.039", "2.206")],
        underemployed_rows=[("32874", "42.918", "34.081"), ("32905", "43.244", "34.085")],
    )
    client = _DefaultNyfedClient(workbook_url="https://example.test/workbook.xlsx", timeout=12)
    opener = _FakeOpener([workbook])
    client._opener = opener  # pyright: ignore[reportPrivateUsage]

    rows = client.fetch_observations(
        provider_series_id="unemployed_recent_graduates",
        start_date=date(1990, 2, 1),
    )

    assert len(rows) == 1
    assert rows[0]["date"] == "1990-02-01"
    assert opener.calls == [("https://example.test/workbook.xlsx", 12)]


def test_nyfed_source_supports_passthrough_records() -> None:
    """Passthrough mode should still validate and ingest canonical records."""
    client = _FakeNyfedClient(rows_by_series={})
    registry, capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=NYFED_COLLEGE_LABOR_MARKET_SOURCE_KEY,
        run_id="run-nyfed-passthrough",
        trigger_type="on_demand",
        run_context={
            "records": [
                {
                    "source_name": "NYFED",
                    "source_key": NYFED_PROVIDER_GROUP_KEY,
                    "source_title": NYFED_SOURCE_TITLE,
                    "source_description": NYFED_SOURCE_DESCRIPTION,
                    "source_type": "external",
                    "series_key": "LABOR.US.TEST",
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

    assert result.status == "success"
    assert result.accepted_count == 1
    assert len(capture_repo.rows) == 1


def test_nyfed_source_maps_grouped_series_and_uses_incremental_start_dates() -> None:
    """Grouped workflow should fetch each configured series with independent checkpoints."""
    rows_by_series = {
        "unemployed_recent_graduates": [
            {"date": "2026-01-01", "reported_at": "2026-02-04T00:00:00Z", "value": "4.1"}
        ],
        "unemployed_college_graduates": [
            {"date": "2026-01-01", "reported_at": "2026-02-04T00:00:00Z", "value": "2.4"}
        ],
        "underemployed_recent_graduates": [
            {"date": "2026-01-01", "reported_at": "2026-02-04T00:00:00Z", "value": "40.1"}
        ],
        "underemployed_college_graduates": [
            {"date": "2026-01-01", "reported_at": "2026-02-04T00:00:00Z", "value": "34.5"}
        ],
    }
    client = _FakeNyfedClient(rows_by_series=rows_by_series)
    registry, capture_repo = _build_registry(
        client=client,
        checkpoint_latest_by_series={
            SERIES_CONFIGS[0]["canonical_series_key"]: date(2025, 12, 1),
            SERIES_CONFIGS[1]["canonical_series_key"]: date(2025, 11, 1),
            SERIES_CONFIGS[2]["canonical_series_key"]: date(2025, 10, 1),
            SERIES_CONFIGS[3]["canonical_series_key"]: date(2025, 9, 1),
        },
    )

    result = registry.execute_for_source(
        source_key=NYFED_COLLEGE_LABOR_MARKET_SOURCE_KEY,
        run_id="run-nyfed-success",
        trigger_type="scheduled",
        run_context={"series_item_keys": [config["series_item_key"] for config in SERIES_CONFIGS]},
    )

    assert result.status == "success"
    assert result.accepted_count == FOUR
    assert len(capture_repo.rows) == FOUR
    start_dates = {call["provider_series_id"]: call["start_date"] for call in client.calls}
    assert start_dates["unemployed_recent_graduates"] == date(2025, 12, 2)
    assert start_dates["unemployed_college_graduates"] == date(2025, 11, 2)
    assert start_dates["underemployed_recent_graduates"] == date(2025, 10, 2)
    assert start_dates["underemployed_college_graduates"] == date(2025, 9, 2)
    assert {str(row.unit_type) for row in capture_repo.rows} == {"percent"}
    assert {str(row.source_key) for row in capture_repo.rows} == {NYFED_PROVIDER_GROUP_KEY}
    assert {str(row.source_title) for row in capture_repo.rows} == {NYFED_SOURCE_TITLE}


def test_nyfed_source_reports_partial_failure_for_series_errors() -> None:
    """Mixed fetch results should return partial success with per-series failures."""
    client = _FakeNyfedClient(
        rows_by_series={
            "unemployed_recent_graduates": [
                {"date": "2026-01-01", "reported_at": "2026-02-04T00:00:00Z", "value": "4.1"}
            ]
        },
        fail_series_ids={
            "unemployed_college_graduates",
            "underemployed_recent_graduates",
            "underemployed_college_graduates",
        },
    )
    registry, _capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=NYFED_COLLEGE_LABOR_MARKET_SOURCE_KEY,
        run_id="run-nyfed-partial",
        trigger_type="on_demand",
        run_context={"series_item_keys": [config["series_item_key"] for config in SERIES_CONFIGS]},
    )

    assert result.status == "partial_success"
    assert result.accepted_count == 1
    assert result.failed_count == THREE


def test_nyfed_source_reports_failure_when_all_series_fail() -> None:
    """If all configured series fail provider retrieval, workflow should fail."""
    client = _FakeNyfedClient(should_fail=True)
    registry, _capture_repo = _build_registry(client=client)

    result = registry.execute_for_source(
        source_key=NYFED_COLLEGE_LABOR_MARKET_SOURCE_KEY,
        run_id="run-nyfed-failure",
        trigger_type="on_demand",
        run_context={"series_item_keys": [config["series_item_key"] for config in SERIES_CONFIGS]},
    )

    assert result.status == "failure"
    assert result.accepted_count == 0
    assert result.failed_count == FOUR
    assert result.outcome_reason_code == "provider_request_failed"
