"""Jail Data Initiative jail population source workflow adapter."""

from __future__ import annotations

import logging
from collections.abc import Iterator, Sequence
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO
from time import perf_counter
from typing import Any, Protocol, cast
from urllib.request import build_opener

import polars as pl

from src.orchestration.jobs.source_assets.discovery import ObservationCheckpointRepository
from src.orchestration.jobs.source_ingest_runner import SourceIngestRunner
from src.orchestration.jobs.source_schedule_policy import SourceSchedulePolicy
from src.orchestration.jobs.workflow_registry import SourceWorkflowRegistration
from src.orchestration.jobs.workflow_request import SourceWorkflowRequest
from src.orchestration.jobs.workflow_result import SourceWorkflowResult

JDI_JAIL_POPULATION_SOURCE_KEY = "jdi_jail_population"
JDI_PROVIDER_GROUP_KEY = "jdi"
JDI_SOURCE_NAME = "JDI"
JDI_SOURCE_TITLE = "Jail Data Initiative Jail Population"
JDI_SOURCE_DESCRIPTION = (
    "Daily jail population time series by roster and US aggregate from Jail Data Initiative."
)
JDI_FULL_DATA_CSV_URL = "https://psl-jdi-public.s3.amazonaws.com/jdi_full_data.csv"
JDI_TOTAL_SERIES_ITEM_KEY = "jdi_jail_population_total"
JDI_TOTAL_CANONICAL_SERIES_KEY = "JUSTICE.US.JAIL_POPULATION.TOTAL"

_ROW_COUNT_MINIMUM = 1000
_PARSE_SUCCESS_RATIO_MINIMUM = Decimal("0.99")
_JDI_REQUIRED_COLUMNS: tuple[str, ...] = (
    "State",
    "Roster_ID",
    "Date",
    "Population_Interpolated",
    "As_Of",
)

JdiRawRows = bytes | str | Sequence[dict[str, str]]

logger = logging.getLogger(__name__)

JDI_WHITELISTED_AGENCY_ROSTERS: tuple[tuple[str, str], ...] = (
    ("CA", "CA-Los_Angeles"),
    ("TX", "TX-Harris"),
    ("TX", "TX-Dallas"),
    ("AZ", "AZ-Maricopa"),
    ("NY", "NY-New_York_City"),
    ("CT", "CT-All"),
    ("WV", "WV-All"),
    ("TX", "TX-Tarrant"),
    ("FL", "FL-Duval"),
    ("CA", "CA-Riverside"),
    ("FL", "FL-Broward"),
    ("CA", "CA-Orange"),
    ("FL", "FL-Hillsborough"),
    ("FL", "FL-Polk"),
    ("FL", "FL-Orange"),
    ("FL", "FL-Pinellas"),
    ("NV", "NV-Clark"),
    ("GA", "GA-Gwinnett"),
    ("TN", "TN-Davidson"),
    ("GA", "GA-Fulton"),
)


class JdiCsvClient(Protocol):
    """Protocol for JDI CSV download adapters."""

    def fetch_observations(self) -> JdiRawRows:
        """Fetch JDI CSV payload from the full dataset export."""
        raise NotImplementedError


class _DefaultJdiCsvClient:
    """HTTP adapter for downloading and parsing JDI CSV exports."""

    def __init__(
        self,
        *,
        csv_url: str = JDI_FULL_DATA_CSV_URL,
        timeout: int = 120,
    ) -> None:
        self._csv_url = csv_url
        self._timeout = timeout
        self._opener = build_opener()

    def fetch_observations(self) -> bytes:
        try:
            with self._opener.open(self._csv_url, timeout=self._timeout) as response:
                return response.read()
        except Exception as exc:  # pragma: no cover - network boundary
            raise RuntimeError("jdi csv request failed") from exc


def _normalize_key_token(raw: str) -> str:
    """Normalize free-form provider text into canonical key token format."""
    normalized_chars = [
        char.upper() if char.isalnum() else "_" for char in raw.strip() if char not in "\n\r\t"
    ]
    collapsed = "".join(normalized_chars)
    while "__" in collapsed:
        collapsed = collapsed.replace("__", "_")
    return collapsed.strip("_")


def _whitelist_series_item_key(*, state: str, roster_id: str) -> str:
    state_token = _normalize_key_token(state).lower() or "unknown"
    roster_token = _normalize_key_token(roster_id).lower() or "unknown"
    series_suffix = (
        roster_token
        if roster_token.startswith(f"{state_token}_")
        else f"{state_token}_{roster_token}"
    )
    return f"jdi_jail_population_{series_suffix}"


def _whitelist_canonical_series_key(*, state: str, roster_id: str) -> str:
    state_token = _normalize_key_token(state) or "UNKNOWN"
    roster_token = _normalize_key_token(roster_id) or "UNKNOWN"
    return f"JUSTICE.US.JAIL_POPULATION.{state_token}.{roster_token}"


JDI_WHITELISTED_SERIES_CONFIGS: tuple[dict[str, str], ...] = tuple(
    {
        "state": state,
        "roster_id": roster_id,
        "state_token": _normalize_key_token(state) or "UNKNOWN",
        "roster_token": _normalize_key_token(roster_id) or "UNKNOWN",
        "series_item_key": _whitelist_series_item_key(state=state, roster_id=roster_id),
        "canonical_series_key": _whitelist_canonical_series_key(state=state, roster_id=roster_id),
    }
    for state, roster_id in JDI_WHITELISTED_AGENCY_ROSTERS
)

JDI_WHITELISTED_SERIES_ITEM_KEYS: tuple[str, ...] = tuple(
    config["series_item_key"] for config in JDI_WHITELISTED_SERIES_CONFIGS
)
JDI_WHITELISTED_CANONICAL_SERIES_KEYS: tuple[str, ...] = tuple(
    config["canonical_series_key"] for config in JDI_WHITELISTED_SERIES_CONFIGS
)
JDI_SUPPORTED_SERIES_ITEM_KEYS: set[str] = {
    *JDI_WHITELISTED_SERIES_ITEM_KEYS,
    JDI_TOTAL_SERIES_ITEM_KEY,
}
JDI_SERIES_ITEM_TO_CANONICAL_KEY: dict[str, str] = {
    config["series_item_key"]: config["canonical_series_key"]
    for config in JDI_WHITELISTED_SERIES_CONFIGS
}
JDI_SERIES_ITEM_TO_CANONICAL_KEY[JDI_TOTAL_SERIES_ITEM_KEY] = JDI_TOTAL_CANONICAL_SERIES_KEY


def _roster_series_key(*, state: str, roster_id: str) -> str:
    state_token = _normalize_key_token(state) or "UNKNOWN"
    roster_token = _normalize_key_token(roster_id) or "UNKNOWN"
    return f"JUSTICE.US.JAIL_POPULATION.{state_token}.{roster_token}"


def _parse_population(raw: str) -> Decimal | None:
    value = raw.strip()
    if value == "":
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _parse_date(raw: str) -> date | None:
    try:
        return date.fromisoformat(raw.strip())
    except ValueError:
        return None


def _coerce_reported_at(raw: str) -> str | None:
    value = raw.strip()
    if value == "":
        return None
    if "T" in value:
        return value
    return value.replace(" ", "T") + "+00:00"


def _format_numeric_value(value: float) -> str:
    rendered = f"{value:.15f}".rstrip("0").rstrip(".")
    return rendered if rendered != "" else "0"


def _load_rows_frame(rows: JdiRawRows) -> pl.DataFrame:
    if isinstance(rows, bytes):
        frame = pl.read_csv(
            BytesIO(rows),
            columns=list(_JDI_REQUIRED_COLUMNS),
            schema_overrides=dict.fromkeys(_JDI_REQUIRED_COLUMNS, pl.Utf8),
        )
        return frame.select(list(_JDI_REQUIRED_COLUMNS))

    if isinstance(rows, str):
        frame = pl.read_csv(
            BytesIO(rows.encode("utf-8")),
            columns=list(_JDI_REQUIRED_COLUMNS),
            schema_overrides=dict.fromkeys(_JDI_REQUIRED_COLUMNS, pl.Utf8),
        )
        return frame.select(list(_JDI_REQUIRED_COLUMNS))

    frame = pl.from_dicts(rows)
    for column in _JDI_REQUIRED_COLUMNS:
        if column not in frame.columns:
            frame = frame.with_columns(pl.lit(None).cast(pl.Utf8).alias(column))

    return frame.select(
        [
            pl.col("State").cast(pl.Utf8, strict=False).alias("State"),
            pl.col("Roster_ID").cast(pl.Utf8, strict=False).alias("Roster_ID"),
            pl.col("Date").cast(pl.Utf8, strict=False).alias("Date"),
            pl.col("Population_Interpolated")
            .cast(pl.Utf8, strict=False)
            .alias("Population_Interpolated"),
            pl.col("As_Of").cast(pl.Utf8, strict=False).alias("As_Of"),
        ]
    )


def _token_expr(column: str) -> pl.Expr:
    return (
        pl.col(column)
        .str.strip_chars()
        .str.to_uppercase()
        .str.replace_all(r"[^A-Z0-9]", "_")
        .str.replace_all(r"_+", "_")
        .str.strip_chars("_")
    )


def _build_records(
    *,
    rows: JdiRawRows,
    observation_repository: ObservationCheckpointRepository,
    requested_series_items: set[str] | None,
) -> tuple[_JdiRecordStream, int]:
    started_at = perf_counter()
    now_iso = datetime.now(tz=UTC).isoformat()
    rows_frame = _load_rows_frame(rows)
    total_rows = rows_frame.height
    logger.warning("jdi adapter: loaded csv rows total_rows=%s", total_rows)

    normalized = rows_frame.with_columns(
        [
            pl.col("State").fill_null("").str.strip_chars().alias("state"),
            pl.col("Roster_ID").fill_null("").str.strip_chars().alias("roster_id"),
            pl.col("Date")
            .fill_null("")
            .str.strip_chars()
            .str.strptime(pl.Date, format="%Y-%m-%d", strict=False)
            .alias("observed_on"),
            pl.col("Population_Interpolated").fill_null("").str.strip_chars().alias("value_raw"),
            pl.col("As_Of").fill_null("").str.strip_chars().alias("as_of_raw"),
        ]
    ).with_columns(
        [
            pl.col("value_raw")
            .str.contains(r"^-?\d+(?:\.\d+)?$")
            .fill_null(False)
            .alias("value_valid"),
            pl.col("value_raw").cast(pl.Float64, strict=False).alias("value_float"),
            _token_expr("state").alias("state_token"),
            _token_expr("roster_id").alias("roster_token"),
            pl.when(pl.col("as_of_raw") == "")
            .then(pl.lit(now_iso))
            .when(pl.col("as_of_raw").str.contains("T"))
            .then(pl.col("as_of_raw"))
            .otherwise(pl.col("as_of_raw").str.replace_all(" ", "T") + pl.lit("+00:00"))
            .alias("reported_at"),
        ]
    )

    parsed = normalized.filter(
        (pl.col("state") != "")
        & (pl.col("roster_id") != "")
        & pl.col("observed_on").is_not_null()
        & pl.col("value_valid")
        & pl.col("value_float").is_not_null()
    )

    parsed_count = parsed.height
    invalid_rows = total_rows - parsed_count
    logger.warning(
        "jdi adapter: parsed rows parsed_rows=%s invalid_rows=%s",
        parsed_count,
        invalid_rows,
    )
    if total_rows < _ROW_COUNT_MINIMUM:
        raise RuntimeError(
            "jdi csv row-count sanity check failed: "
            f"total_rows={total_rows} minimum={_ROW_COUNT_MINIMUM}"
        )
    success_ratio = Decimal(parsed_count) / Decimal(total_rows)
    if success_ratio < _PARSE_SUCCESS_RATIO_MINIMUM:
        raise RuntimeError(
            "jdi csv parse-success check failed: "
            f"parsed_rows={parsed_count} invalid_rows={invalid_rows} "
            f"success_ratio={success_ratio} minimum={_PARSE_SUCCESS_RATIO_MINIMUM}"
        )

    whitelist_frame = pl.from_dicts(
        [
            {
                "state_token": config["state_token"],
                "roster_token": config["roster_token"],
                "series_item_key": config["series_item_key"],
                "series_key": config["canonical_series_key"],
                "roster_id": config["roster_id"],
                "state": config["state"],
            }
            for config in JDI_WHITELISTED_SERIES_CONFIGS
            if requested_series_items is None or config["series_item_key"] in requested_series_items
        ],
        schema={
            "state_token": pl.Utf8,
            "roster_token": pl.Utf8,
            "series_item_key": pl.Utf8,
            "series_key": pl.Utf8,
            "roster_id": pl.Utf8,
            "state": pl.Utf8,
        },
    )

    unique_series_keys = sorted(whitelist_frame.get_column("series_key").to_list())
    logger.warning(
        "jdi adapter: selected whitelisted series count=%s",
        len(unique_series_keys),
    )
    latest_by_series: dict[str, date | None] = {
        series_key: observation_repository.read_latest_observed_on(series_key=series_key)
        for series_key in unique_series_keys
    }
    latest_total = observation_repository.read_latest_observed_on(
        series_key=JDI_TOTAL_CANONICAL_SERIES_KEY
    )

    agency_rows = parsed.join(whitelist_frame, on=["state_token", "roster_token"], how="inner")
    include_total_series = (
        requested_series_items is None or JDI_TOTAL_SERIES_ITEM_KEY in requested_series_items
    )

    latest_rows = [
        {"series_key": series_key, "latest_observed_on": latest}
        for series_key, latest in latest_by_series.items()
    ]
    latest_frame = (
        pl.from_dicts(latest_rows)
        if latest_rows
        else pl.DataFrame(schema={"series_key": pl.Utf8, "latest_observed_on": pl.Date})
    )

    agency_fresh = agency_rows.join(latest_frame, on="series_key", how="left").filter(
        pl.col("latest_observed_on").is_null()
        | (pl.col("observed_on") > pl.col("latest_observed_on"))
    )
    logger.warning("jdi adapter: incremental agency rows fresh_rows=%s", agency_fresh.height)

    total_by_day = pl.DataFrame(
        schema={
            "observed_on": pl.Date,
            "total_value": pl.Float64,
            "reported_at": pl.Utf8,
        }
    )
    if include_total_series:
        total_by_day = parsed.group_by("observed_on").agg(
            [
                pl.col("value_float").sum().alias("total_value"),
                pl.col("reported_at").max().alias("reported_at"),
            ]
        )
        if latest_total is not None:
            total_by_day = total_by_day.filter(pl.col("observed_on") > pl.lit(latest_total))

    roster_record_count = agency_fresh.height
    total_record_count = total_by_day.height
    dynamic_series_count = (
        len(agency_fresh.get_column("series_key").unique().to_list())
        if roster_record_count > 0
        else 0
    )

    logger.warning(
        (
            "jdi adapter: built records roster_records=%s total_records=%s "
            "total_output_records=%s elapsed_seconds=%.2f"
        ),
        roster_record_count,
        total_record_count,
        roster_record_count + total_record_count,
        perf_counter() - started_at,
    )

    return (
        _JdiRecordStream(
            agency_rows=agency_fresh,
            total_rows=total_by_day.sort("observed_on"),
            now_iso=now_iso,
        ),
        dynamic_series_count,
    )


class _JdiRecordStream:
    def __init__(
        self,
        *,
        agency_rows: pl.DataFrame,
        total_rows: pl.DataFrame,
        now_iso: str,
    ) -> None:
        self._agency_rows = agency_rows
        self._total_rows = total_rows
        self._now_iso = now_iso

    def __len__(self) -> int:
        return self._agency_rows.height + self._total_rows.height

    def __iter__(self) -> Iterator[dict[str, object]]:
        for row in self._agency_rows.iter_rows(named=True):
            observed_on = row["observed_on"]
            assert isinstance(observed_on, date)
            roster_id = str(row["roster_id"])
            state = str(row["state"])
            metric_name = f"Daily Jail Population - {roster_id}"
            value_float = row["value_float"]
            assert isinstance(value_float, float)
            yield {
                "source_name": JDI_SOURCE_NAME,
                "source_key": JDI_PROVIDER_GROUP_KEY,
                "source_title": JDI_SOURCE_TITLE,
                "source_description": JDI_SOURCE_DESCRIPTION,
                "source_type": "external",
                "series_key": str(row["series_key"]),
                "metric_name": metric_name,
                "dataset_title": metric_name,
                "dataset_description": (
                    f"Daily jail population for roster {roster_id} published by "
                    "the Jail Data Initiative."
                ),
                "dataset_geographic_scope": state,
                "topic_tags": ["justice", "jail", "population", "incarceration", "daily"],
                "frequency": "daily",
                "date": observed_on.isoformat(),
                "reported_at": str(row["reported_at"]),
                "value": _format_numeric_value(value_float),
                "unit": "people",
                "unit_type": "number",
                "attributes": {
                    "provider_series_id": roster_id,
                    "provider_state": state,
                },
            }

        for row in self._total_rows.iter_rows(named=True):
            observed_on = row["observed_on"]
            assert isinstance(observed_on, date)
            total_value = row["total_value"]
            assert isinstance(total_value, float)
            yield {
                "source_name": JDI_SOURCE_NAME,
                "source_key": JDI_PROVIDER_GROUP_KEY,
                "source_title": JDI_SOURCE_TITLE,
                "source_description": JDI_SOURCE_DESCRIPTION,
                "source_type": "external",
                "series_key": JDI_TOTAL_CANONICAL_SERIES_KEY,
                "metric_name": "Daily Jail Population - Total",
                "dataset_title": "Daily Jail Population - Total",
                "dataset_description": (
                    "Daily aggregate jail population total across all JDI rosters in the full "
                    "historical export."
                ),
                "dataset_geographic_scope": "United States",
                "topic_tags": ["justice", "jail", "population", "incarceration", "daily"],
                "frequency": "daily",
                "date": observed_on.isoformat(),
                "reported_at": str(row["reported_at"] or self._now_iso),
                "value": _format_numeric_value(total_value),
                "unit": "people",
                "unit_type": "number",
                "attributes": {"provider_series_id": "TOTAL"},
            }


def _map_jdi_records(
    *,
    rows: JdiRawRows,
    observation_repository: ObservationCheckpointRepository,
    requested_series_items: set[str] | None,
) -> tuple[_JdiRecordStream, int]:
    """Map raw JDI CSV rows to canonical observation payloads."""
    return _build_records(
        rows=rows,
        observation_repository=observation_repository,
        requested_series_items=requested_series_items,
    )


def build_jdi_jail_population_source_workflow(
    runner: SourceIngestRunner,
    *,
    observation_repository: ObservationCheckpointRepository,
    client: JdiCsvClient | None = None,
    schedule_policy: SourceSchedulePolicy | None = None,
) -> SourceWorkflowRegistration:
    """Build workflow registration for jdi_jail_population."""
    jdi_client = client or _DefaultJdiCsvClient()

    def _handler(request: SourceWorkflowRequest) -> SourceWorkflowResult:
        handler_started_at = perf_counter()
        runner.sync_source_metadata(
            source_key=JDI_PROVIDER_GROUP_KEY,
            source_name=JDI_SOURCE_NAME,
            source_title=JDI_SOURCE_TITLE,
            source_description=JDI_SOURCE_DESCRIPTION,
            source_type="external",
        )

        passthrough_records = request.run_context.get("records")
        if passthrough_records is not None:
            if not isinstance(passthrough_records, list):
                raise ValueError("run_context.records must be a list")
            return runner.run_records(request=request, records=passthrough_records)

        requested_series_items_raw = request.run_context.get("series_item_keys")
        requested_series_items = (
            {
                value.strip()
                for value in requested_series_items_raw
                if isinstance(value, str) and value.strip() != ""
            }
            if isinstance(requested_series_items_raw, list)
            else None
        )
        selected_series_items = (
            requested_series_items.intersection(JDI_SUPPORTED_SERIES_ITEM_KEYS)
            if requested_series_items is not None
            else None
        )
        if requested_series_items is not None and not selected_series_items:
            return SourceWorkflowResult(
                source_key=request.source_key,
                status="success",
                accepted_count=0,
                quarantined_count=0,
                failed_count=0,
                series_outcomes=[],
            )

        include_total_series = (
            selected_series_items is None or JDI_TOTAL_SERIES_ITEM_KEY in selected_series_items
        )
        fallback_series_keys = [JDI_TOTAL_CANONICAL_SERIES_KEY] if include_total_series else None
        if include_total_series:
            outcome_series_item_key = JDI_TOTAL_SERIES_ITEM_KEY
        else:
            assert selected_series_items is not None
            outcome_series_item_key = sorted(selected_series_items)[0]
        outcome_canonical_series_key = JDI_SERIES_ITEM_TO_CANONICAL_KEY.get(
            outcome_series_item_key,
            JDI_TOTAL_CANONICAL_SERIES_KEY,
        )
        outcome_provider_series_id = (
            "TOTAL"
            if outcome_series_item_key == JDI_TOTAL_SERIES_ITEM_KEY
            else outcome_series_item_key
        )

        try:
            logger.warning("jdi adapter: fetching provider data")
            raw_rows = jdi_client.fetch_observations()
            logger.warning(
                "jdi adapter: fetched provider data payload_type=%s",
                type(raw_rows).__name__,
            )
            records = _map_jdi_records(
                rows=raw_rows,
                observation_repository=observation_repository,
                requested_series_items=selected_series_items,
            )
            stream, dynamic_series_count = records
            logger.warning("jdi adapter: mapped records output_count=%s", len(stream))
        except Exception as exc:
            return SourceWorkflowResult(
                source_key=request.source_key,
                status="failure",
                accepted_count=0,
                quarantined_count=0,
                failed_count=1,
                outcome_reason_code="provider_request_failed",
                message=str(exc),
                series_outcomes=[
                    {
                        "series_item_key": outcome_series_item_key,
                        "canonical_series_key": outcome_canonical_series_key,
                        "provider_series_id": outcome_provider_series_id,
                        "provider_group_key": JDI_PROVIDER_GROUP_KEY,
                        "ownership_mode": "grouped",
                        "owner_adapter_key": request.source_key,
                        "status": "failure",
                        "accepted_count": 0,
                        "quarantined_count": 0,
                        "failed_count": 1,
                        "outcome_reason_code": "provider_request_failed",
                        "message": str(exc),
                    }
                ],
            )

        logger.warning("jdi adapter: starting run_records record_count=%s", len(stream))
        run_records_started_at = perf_counter()
        result = runner.run_records(
            request=request,
            records=cast(list[dict[str, object]], stream),
            fallback_series_keys=fallback_series_keys,
        )
        logger.warning(
            (
                "jdi adapter: completed run_records status=%s accepted=%s "
                "quarantined=%s failed=%s elapsed_seconds=%.2f "
                "total_handler_seconds=%.2f"
            ),
            result.status,
            result.accepted_count,
            result.quarantined_count,
            result.failed_count,
            perf_counter() - run_records_started_at,
            perf_counter() - handler_started_at,
        )
        return SourceWorkflowResult(
            source_key=request.source_key,
            status=result.status,
            accepted_count=result.accepted_count,
            quarantined_count=result.quarantined_count,
            failed_count=result.failed_count,
            outcome_reason_code=result.outcome_reason_code,
            message=result.message,
            series_outcomes=[
                {
                    "series_item_key": outcome_series_item_key,
                    "canonical_series_key": outcome_canonical_series_key,
                    "provider_series_id": outcome_provider_series_id,
                    "provider_group_key": JDI_PROVIDER_GROUP_KEY,
                    "ownership_mode": "grouped",
                    "owner_adapter_key": request.source_key,
                    "status": result.status,
                    "accepted_count": result.accepted_count,
                    "quarantined_count": result.quarantined_count,
                    "failed_count": result.failed_count,
                    "dynamic_series_count": dynamic_series_count,
                }
            ],
            cadence_decisions=result.cadence_decisions,
        )

    return SourceWorkflowRegistration(
        workflow_id="wf-jdi-jail-population",
        source_key=JDI_JAIL_POPULATION_SOURCE_KEY,
        owner="pipeline",
        supported_trigger_modes={"scheduled", "on_demand"},
        handler=_handler,
        schedule_policy=schedule_policy,
    )


SOURCE_SPEC: dict[str, Any] = {
    "source_key": JDI_JAIL_POPULATION_SOURCE_KEY,
    "provider_group_key": JDI_PROVIDER_GROUP_KEY,
    "title": JDI_SOURCE_TITLE,
    "description": JDI_SOURCE_DESCRIPTION,
    "series_item_keys": (*JDI_WHITELISTED_SERIES_ITEM_KEYS, JDI_TOTAL_SERIES_ITEM_KEY),
    "canonical_series_keys": (
        *JDI_WHITELISTED_CANONICAL_SERIES_KEYS,
        JDI_TOTAL_CANONICAL_SERIES_KEY,
    ),
    "ownership_mode": "grouped",
    "cron_schedule": "0 7 * * *",
    "cadence_label": "daily",
    "builder": build_jdi_jail_population_source_workflow,
}
