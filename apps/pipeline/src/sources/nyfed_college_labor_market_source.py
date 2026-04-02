"""NY Fed college labor market source workflow adapter."""

from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta
from io import BytesIO
from time import strptime
from typing import Any, Protocol
from urllib.request import build_opener

import polars as pl

from src.orchestration.jobs.source_assets.discovery import ObservationCheckpointRepository
from src.orchestration.jobs.source_ingest_runner import SourceIngestRunner
from src.orchestration.jobs.source_schedule_policy import SourceSchedulePolicy
from src.orchestration.jobs.workflow_registry import SourceWorkflowRegistration
from src.orchestration.jobs.workflow_request import SourceWorkflowRequest
from src.orchestration.jobs.workflow_result import SourceWorkflowResult

NYFED_COLLEGE_LABOR_MARKET_SOURCE_KEY = "nyfed_college_labor_market"
NYFED_PROVIDER_GROUP_KEY = "nyfed"
NYFED_SOURCE_NAME = "NYFED"
NYFED_SOURCE_TITLE = "New York Fed College Labor Market"
NYFED_SOURCE_DESCRIPTION = (
    "College labor market unemployment and underemployment time series "
    "published by the New York Fed."
)
NYFED_COLLEGE_LABOR_MARKET_URL = (
    "https://www.newyorkfed.org/medialibrary/Research/Interactives/Data/"
    "college-labor-market/College-labor-data"
)
_SHEET_NAMES = {"unemployed", "underemployed"}
_EXCEL_EPOCH = datetime(1899, 12, 30, tzinfo=UTC)
_EXPECTED_HEADERS: dict[str, tuple[str, ...]] = {
    "unemployed": (
        "Date",
        "Young workers",
        "All workers",
        "Recent graduates",
        "College graduates",
    ),
    "underemployed": ("Date", "Recent graduates", "College graduates"),
}

SERIES_CONFIGS: tuple[dict[str, Any], ...] = (
    {
        "series_item_key": "nyfed_recent_graduate_unemployment",
        "provider_series_id": "unemployed_recent_graduates",
        "canonical_series_key": "LABOR.US.NYFED.RECENT_COLLEGE_GRAD_UNEMPLOYMENT",
        "metric_name": "Recent College Graduates Unemployment Rate",
        "dataset_description": (
            "Monthly unemployment rate for recent college graduates from the New York Fed "
            "College Labor Market workbook."
        ),
        "dataset_geographic_scope": "United States",
        "topic_tags": ["labor", "unemployment", "college graduates", "recent graduates", "ny fed"],
        "frequency": "monthly",
        "sheet_name": "unemployed",
        "value_column": "D",
        "unit": "Percent",
        "unit_type": "percent",
    },
    {
        "series_item_key": "nyfed_college_graduate_unemployment",
        "provider_series_id": "unemployed_college_graduates",
        "canonical_series_key": "LABOR.US.NYFED.COLLEGE_GRAD_UNEMPLOYMENT",
        "metric_name": "College Graduates Unemployment Rate",
        "dataset_description": (
            "Monthly unemployment rate for college graduates from the New York Fed "
            "College Labor Market workbook."
        ),
        "dataset_geographic_scope": "United States",
        "topic_tags": ["labor", "unemployment", "college graduates", "ny fed"],
        "frequency": "monthly",
        "sheet_name": "unemployed",
        "value_column": "E",
        "unit": "Percent",
        "unit_type": "percent",
    },
    {
        "series_item_key": "nyfed_recent_graduate_underemployment",
        "provider_series_id": "underemployed_recent_graduates",
        "canonical_series_key": "LABOR.US.NYFED.RECENT_COLLEGE_GRAD_UNDEREMPLOYMENT",
        "metric_name": "Recent College Graduates Underemployment Rate",
        "dataset_description": (
            "Monthly underemployment rate for recent college graduates from the New York Fed "
            "College Labor Market workbook."
        ),
        "dataset_geographic_scope": "United States",
        "topic_tags": [
            "labor",
            "underemployment",
            "college graduates",
            "recent graduates",
            "ny fed",
        ],
        "frequency": "monthly",
        "sheet_name": "underemployed",
        "value_column": "B",
        "unit": "Percent",
        "unit_type": "percent",
    },
    {
        "series_item_key": "nyfed_college_graduate_underemployment",
        "provider_series_id": "underemployed_college_graduates",
        "canonical_series_key": "LABOR.US.NYFED.COLLEGE_GRAD_UNDEREMPLOYMENT",
        "metric_name": "College Graduates Underemployment Rate",
        "dataset_description": (
            "Monthly underemployment rate for college graduates from the New York Fed "
            "College Labor Market workbook."
        ),
        "dataset_geographic_scope": "United States",
        "topic_tags": ["labor", "underemployment", "college graduates", "ny fed"],
        "frequency": "monthly",
        "sheet_name": "underemployed",
        "value_column": "C",
        "unit": "Percent",
        "unit_type": "percent",
    },
)


class NyfedClient(Protocol):
    """Protocol for NY Fed workbook fetch adapters."""

    def fetch_observations(
        self,
        *,
        provider_series_id: str,
        start_date: date | None,
    ) -> list[dict[str, Any]]:
        """Fetch observation rows for one configured workbook series."""


def _excel_serial_to_date(raw_value: str) -> date:
    try:
        serial = float(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"invalid Excel date serial: {raw_value}") from exc
    return (_EXCEL_EPOCH + timedelta(days=serial)).date()


def _parse_observed_on(raw_value: str) -> date:
    stripped = raw_value.strip()
    if stripped == "":
        raise RuntimeError("missing workbook observation date")
    try:
        return _excel_serial_to_date(stripped)
    except RuntimeError:
        pass
    try:
        return datetime.fromisoformat(stripped).date()
    except ValueError as exc:
        raise RuntimeError(f"invalid workbook observation date: {raw_value}") from exc


def _parse_updated_at(raw_value: str) -> datetime:
    match = re.search(r"Updated:\s*(.+)$", raw_value.strip())
    if match is None:
        raise RuntimeError("missing workbook updated timestamp")
    try:
        parsed = strptime(match.group(1).strip(), "%B %d, %Y")
    except ValueError as exc:
        raise RuntimeError("invalid workbook updated timestamp") from exc
    return datetime(parsed.tm_year, parsed.tm_mon, parsed.tm_mday, tzinfo=UTC)


def _excel_column_name(column_letter: str) -> str:
    index = 0
    for character in column_letter.strip().upper():
        if not ("A" <= character <= "Z"):
            raise RuntimeError(f"invalid Excel column letter: {column_letter}")
        index = (index * 26) + (ord(character) - ord("A") + 1)
    return f"column_{index}"


def _read_sheet_frame(workbook_bytes: bytes, *, sheet_name: str) -> pl.DataFrame:
    try:
        return pl.read_excel(
            BytesIO(workbook_bytes),
            sheet_name=sheet_name,
            engine="calamine",
            has_header=False,
            drop_empty_rows=False,
            drop_empty_cols=False,
        )
    except Exception as exc:
        raise RuntimeError(f"failed to read NY Fed sheet {sheet_name}") from exc


def _resolve_sheet_markers(
    frame: pl.DataFrame,
    *,
    sheet_name: str,
) -> tuple[int, str | None]:
    expected_headers = _EXPECTED_HEADERS[sheet_name]
    header_index: int | None = None
    updated_value: str | None = None
    for index, row in enumerate(frame.iter_rows(named=False)):
        first_cell = row[0] if row else None
        if (
            updated_value is None
            and isinstance(first_cell, str)
            and first_cell.startswith("Updated:")
        ):
            updated_value = first_cell
        if tuple(row[: len(expected_headers)]) == expected_headers:
            header_index = index
            break
    if header_index is None:
        raise RuntimeError(f"unexpected headers in sheet {sheet_name}")
    return header_index, updated_value


def _append_sheet_rows(
    *,
    rows_by_series: dict[str, list[dict[str, Any]]],
    data_frame: pl.DataFrame,
    sheet_name: str,
    reported_at: datetime,
) -> int:
    target_configs = [config for config in SERIES_CONFIGS if config["sheet_name"] == sheet_name]
    for row in data_frame.iter_rows(named=True):
        raw_date = row.get("column_1")
        if not isinstance(raw_date, str):
            raise RuntimeError(f"missing required date value in sheet {sheet_name}")
        observed_on = _parse_observed_on(raw_date)

        for config in target_configs:
            column_name = _excel_column_name(str(config["value_column"]))
            raw_value = row.get(column_name)
            if raw_value is None:
                raise RuntimeError(
                    f"missing required value for sheet {sheet_name} column {config['value_column']}"
                )
            value_str = str(raw_value).strip()
            if value_str == "":
                raise RuntimeError(
                    f"missing required value for sheet {sheet_name} column {config['value_column']}"
                )
            try:
                float(value_str)
            except ValueError as exc:
                raise RuntimeError(
                    "invalid numeric value "
                    f"for sheet {sheet_name} column {config['value_column']}: {value_str}"
                ) from exc
            rows_by_series[config["provider_series_id"]].append(
                {
                    "date": observed_on.isoformat(),
                    "reported_at": reported_at.isoformat(),
                    "value": value_str,
                }
            )

    return data_frame.height


def _parse_workbook_bytes(workbook_bytes: bytes) -> dict[str, list[dict[str, Any]]]:
    rows_by_series: dict[str, list[dict[str, Any]]] = {
        config["provider_series_id"]: [] for config in SERIES_CONFIGS
    }
    row_count_by_sheet: dict[str, int] = {}
    reported_at: datetime | None = None

    for sheet_name in sorted(_SHEET_NAMES):
        frame = _read_sheet_frame(workbook_bytes, sheet_name=sheet_name)
        header_index, updated_value = _resolve_sheet_markers(frame, sheet_name=sheet_name)
        if updated_value is None and reported_at is None:
            raise RuntimeError("missing NY Fed workbook updated row")
        if reported_at is None and updated_value is not None:
            reported_at = _parse_updated_at(updated_value)
        if reported_at is None:
            raise RuntimeError("missing NY Fed workbook updated row")

        data_frame = frame.slice(header_index + 1).filter(
            pl.col("column_1").is_not_null() & (pl.col("column_1").str.len_chars() > 0)
        )
        if data_frame.height == 0:
            raise RuntimeError(f"sheet {sheet_name} contains no data rows")

        row_count_by_sheet[sheet_name] = _append_sheet_rows(
            rows_by_series=rows_by_series,
            data_frame=data_frame,
            sheet_name=sheet_name,
            reported_at=reported_at,
        )

    if len(set(row_count_by_sheet.values())) != 1:
        raise RuntimeError("NY Fed workbook row counts differ across target sheets")

    return rows_by_series


class _DefaultNyfedClient:
    """HTTP adapter for fetching and parsing the NY Fed workbook."""

    def __init__(
        self,
        *,
        workbook_url: str = NYFED_COLLEGE_LABOR_MARKET_URL,
        timeout: int = 30,
    ) -> None:
        self._workbook_url = workbook_url
        self._timeout = timeout
        self._opener = build_opener()

    def fetch_observations(
        self,
        *,
        provider_series_id: str,
        start_date: date | None,
    ) -> list[dict[str, Any]]:
        try:
            with self._opener.open(self._workbook_url, timeout=self._timeout) as response:
                workbook_bytes = response.read()
        except Exception as exc:  # pragma: no cover - network boundary
            raise RuntimeError("nyfed workbook request failed") from exc

        rows_by_series = _parse_workbook_bytes(workbook_bytes)
        series_rows = rows_by_series.get(provider_series_id)
        if series_rows is None:
            raise RuntimeError(f"unknown NY Fed provider series id: {provider_series_id}")
        if start_date is None:
            return series_rows
        return [row for row in series_rows if date.fromisoformat(str(row["date"])) >= start_date]


def _map_records(
    *,
    rows: Sequence[dict[str, Any]],
    series_config: dict[str, Any],
) -> list[dict[str, object]]:
    mapped: list[dict[str, object]] = []
    now_iso = datetime.now(tz=UTC).isoformat()
    for row in rows:
        mapped.append(
            {
                "source_name": NYFED_SOURCE_NAME,
                "source_key": NYFED_PROVIDER_GROUP_KEY,
                "source_title": NYFED_SOURCE_TITLE,
                "source_description": NYFED_SOURCE_DESCRIPTION,
                "source_type": "external",
                "series_key": series_config["canonical_series_key"],
                "metric_name": series_config["metric_name"],
                "dataset_title": series_config["metric_name"],
                "dataset_description": series_config["dataset_description"],
                "dataset_geographic_scope": series_config["dataset_geographic_scope"],
                "topic_tags": series_config["topic_tags"],
                "frequency": series_config["frequency"],
                "date": str(row.get("date", "")),
                "reported_at": str(row.get("reported_at") or now_iso),
                "value": str(row.get("value", "")),
                "unit": series_config["unit"],
                "unit_type": series_config["unit_type"],
                "attributes": {
                    "provider_series_id": series_config["provider_series_id"],
                    "provider_sheet_name": series_config["sheet_name"],
                    "provider_column": series_config["value_column"],
                },
            }
        )
    return mapped


def build_nyfed_college_labor_market_source_workflow(
    runner: SourceIngestRunner,
    *,
    observation_repository: ObservationCheckpointRepository,
    client: NyfedClient | None = None,
    schedule_policy: SourceSchedulePolicy | None = None,
) -> SourceWorkflowRegistration:
    """Build workflow registration for NY Fed college labor market ingestion."""
    nyfed_client = client or _DefaultNyfedClient()

    def _handler(request: SourceWorkflowRequest) -> SourceWorkflowResult:
        runner.sync_source_metadata(
            source_key=NYFED_PROVIDER_GROUP_KEY,
            source_name=NYFED_SOURCE_NAME,
            source_title=NYFED_SOURCE_TITLE,
            source_description=NYFED_SOURCE_DESCRIPTION,
            source_type="external",
        )
        passthrough_records = request.run_context.get("records")
        if passthrough_records is not None:
            if not isinstance(passthrough_records, list):
                raise ValueError("run_context.records must be a list")
            return runner.run_records(request=request, records=passthrough_records)

        accepted_count = 0
        quarantined_count = 0
        failed_count = 0
        series_outcomes: list[dict[str, object]] = []

        requested_series_items_raw = request.run_context.get("series_item_keys")
        requested_series_items = (
            set(requested_series_items_raw)
            if isinstance(requested_series_items_raw, list)
            else None
        )

        for series_config in SERIES_CONFIGS:
            if (
                requested_series_items is not None
                and series_config["series_item_key"] not in requested_series_items
            ):
                continue

            latest = observation_repository.read_latest_observed_on(
                series_key=series_config["canonical_series_key"]
            )
            start_date = latest + timedelta(days=1) if latest is not None else None

            try:
                raw_rows = nyfed_client.fetch_observations(
                    provider_series_id=series_config["provider_series_id"],
                    start_date=start_date,
                )
            except Exception as exc:
                failed_count += 1
                series_outcomes.append(
                    {
                        "series_item_key": series_config["series_item_key"],
                        "canonical_series_key": series_config["canonical_series_key"],
                        "provider_series_id": series_config["provider_series_id"],
                        "provider_group_key": "nyfed",
                        "ownership_mode": "grouped",
                        "owner_adapter_key": request.source_key,
                        "status": "failure",
                        "accepted_count": 0,
                        "quarantined_count": 0,
                        "failed_count": 1,
                        "outcome_reason_code": "provider_request_failed",
                        "message": str(exc),
                    }
                )
                continue

            result = runner.run_records(
                request=request,
                records=_map_records(rows=raw_rows, series_config=series_config),
                fallback_series_keys=[series_config["canonical_series_key"]],
            )
            accepted_count += result.accepted_count
            quarantined_count += result.quarantined_count
            failed_count += result.failed_count
            series_outcomes.append(
                {
                    "series_item_key": series_config["series_item_key"],
                    "canonical_series_key": series_config["canonical_series_key"],
                    "provider_series_id": series_config["provider_series_id"],
                    "provider_group_key": "nyfed",
                    "ownership_mode": "grouped",
                    "owner_adapter_key": request.source_key,
                    "status": result.status,
                    "accepted_count": result.accepted_count,
                    "quarantined_count": result.quarantined_count,
                    "failed_count": result.failed_count,
                }
            )

        status = "success"
        outcome_reason: str | None = None
        message: str | None = None
        if failed_count > 0 and accepted_count == 0 and quarantined_count == 0:
            status = "failure"
            outcome_reason = "provider_request_failed"
            message = "all configured NY Fed series failed provider retrieval"
        elif failed_count > 0 or quarantined_count > 0:
            status = "partial_success"

        return SourceWorkflowResult(
            source_key=request.source_key,
            status=status,
            accepted_count=accepted_count,
            quarantined_count=quarantined_count,
            failed_count=failed_count,
            outcome_reason_code=outcome_reason,
            message=message,
            series_outcomes=series_outcomes,
        )

    return SourceWorkflowRegistration(
        workflow_id="wf-nyfed-college-labor-market",
        source_key=NYFED_COLLEGE_LABOR_MARKET_SOURCE_KEY,
        owner="pipeline",
        supported_trigger_modes={"scheduled", "on_demand"},
        handler=_handler,
        schedule_policy=schedule_policy,
    )


SOURCE_SPEC: dict[str, Any] = {
    "source_key": NYFED_COLLEGE_LABOR_MARKET_SOURCE_KEY,
    "provider_group_key": "nyfed",
    "title": NYFED_SOURCE_TITLE,
    "description": NYFED_SOURCE_DESCRIPTION,
    "series_item_keys": tuple(config["series_item_key"] for config in SERIES_CONFIGS),
    "canonical_series_keys": tuple(config["canonical_series_key"] for config in SERIES_CONFIGS),
    "ownership_mode": "grouped",
    "cron_schedule": "0 0 1 * *",
    "cadence_label": "monthly",
    "builder": build_nyfed_college_labor_market_source_workflow,
}
