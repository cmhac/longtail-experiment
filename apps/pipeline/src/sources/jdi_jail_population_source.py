"""Jail Data Initiative jail population source workflow adapter."""

from __future__ import annotations

import csv
import io
from collections import defaultdict
from collections.abc import Sequence
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Protocol
from urllib.request import build_opener

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


class JdiCsvClient(Protocol):
    """Protocol for JDI CSV download adapters."""

    def fetch_observations(self) -> list[dict[str, str]]:
        """Fetch and parse CSV rows from the JDI full dataset export."""
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

    def fetch_observations(self) -> list[dict[str, str]]:
        try:
            with self._opener.open(self._csv_url, timeout=self._timeout) as response:
                raw_csv = response.read().decode("utf-8")
        except Exception as exc:  # pragma: no cover - network boundary
            raise RuntimeError("jdi csv request failed") from exc

        reader = csv.DictReader(io.StringIO(raw_csv))
        return [dict(row) for row in reader]


def _normalize_key_token(raw: str) -> str:
    """Normalize free-form provider text into canonical key token format."""
    normalized_chars = [
        char.upper() if char.isalnum() else "_" for char in raw.strip() if char not in "\n\r\t"
    ]
    collapsed = "".join(normalized_chars)
    while "__" in collapsed:
        collapsed = collapsed.replace("__", "_")
    return collapsed.strip("_")


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


def _build_records(
    *,
    rows: Sequence[dict[str, str]],
    observation_repository: ObservationCheckpointRepository,
) -> list[dict[str, object]]:
    now_iso = datetime.now(tz=UTC).isoformat()
    parsed_rows: list[dict[str, object]] = []
    invalid_rows = 0

    for row in rows:
        state = str(row.get("State", "")).strip()
        roster_id = str(row.get("Roster_ID", "")).strip()
        observed_on = _parse_date(str(row.get("Date", "")))
        value = _parse_population(str(row.get("Population_Interpolated", "")))
        reported_at = _coerce_reported_at(str(row.get("As_Of", ""))) or now_iso

        if state == "" or roster_id == "" or observed_on is None or value is None:
            invalid_rows += 1
            continue

        series_key = _roster_series_key(state=state, roster_id=roster_id)
        parsed_rows.append(
            {
                "state": state,
                "roster_id": roster_id,
                "series_key": series_key,
                "date": observed_on,
                "reported_at": reported_at,
                "value": value,
            }
        )

    total_rows = len(rows)
    parsed_count = len(parsed_rows)
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

    unique_series_keys = sorted({str(item["series_key"]) for item in parsed_rows})
    latest_by_series: dict[str, date | None] = {
        series_key: observation_repository.read_latest_observed_on(series_key=series_key)
        for series_key in unique_series_keys
    }
    latest_total = observation_repository.read_latest_observed_on(
        series_key=JDI_TOTAL_CANONICAL_SERIES_KEY
    )

    records: list[dict[str, object]] = []
    total_by_day: dict[date, Decimal] = defaultdict(lambda: Decimal("0"))
    reported_at_by_day: dict[date, str] = {}

    for item in parsed_rows:
        series_key = str(item["series_key"])
        observed_on = item["date"]
        assert isinstance(observed_on, date)
        latest = latest_by_series.get(series_key)
        if latest is not None and observed_on <= latest:
            continue

        value = item["value"]
        assert isinstance(value, Decimal)
        total_by_day[observed_on] += value
        reported_at = str(item["reported_at"])
        reported_at_by_day[observed_on] = max(reported_at_by_day.get(observed_on, ""), reported_at)

        roster_id = str(item["roster_id"])
        state = str(item["state"])
        metric_name = f"Daily Jail Population - {roster_id}"
        records.append(
            {
                "source_name": JDI_SOURCE_NAME,
                "source_key": JDI_PROVIDER_GROUP_KEY,
                "source_title": JDI_SOURCE_TITLE,
                "source_description": JDI_SOURCE_DESCRIPTION,
                "source_type": "external",
                "series_key": series_key,
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
                "reported_at": reported_at,
                "value": str(value),
                "unit": "people",
                "unit_type": "number",
                "attributes": {
                    "provider_series_id": roster_id,
                    "provider_state": state,
                },
            }
        )

    for observed_on, value in sorted(total_by_day.items()):
        if latest_total is not None and observed_on <= latest_total:
            continue
        records.append(
            {
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
                "reported_at": reported_at_by_day.get(observed_on, now_iso),
                "value": str(value),
                "unit": "people",
                "unit_type": "number",
                "attributes": {"provider_series_id": "TOTAL"},
            }
        )

    return records


def _map_jdi_records(
    *,
    rows: Sequence[dict[str, str]],
    observation_repository: ObservationCheckpointRepository,
) -> list[dict[str, object]]:
    """Map raw JDI CSV rows to canonical observation payloads."""
    return _build_records(rows=rows, observation_repository=observation_repository)


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
        if (
            requested_series_items is not None
            and JDI_TOTAL_SERIES_ITEM_KEY not in requested_series_items
        ):
            return SourceWorkflowResult(
                source_key=request.source_key,
                status="success",
                accepted_count=0,
                quarantined_count=0,
                failed_count=0,
                series_outcomes=[],
            )

        try:
            raw_rows = jdi_client.fetch_observations()
            records = _map_jdi_records(
                rows=raw_rows,
                observation_repository=observation_repository,
            )
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
                        "series_item_key": JDI_TOTAL_SERIES_ITEM_KEY,
                        "canonical_series_key": JDI_TOTAL_CANONICAL_SERIES_KEY,
                        "provider_series_id": "TOTAL",
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

        result = runner.run_records(
            request=request,
            records=records,
            fallback_series_keys=[JDI_TOTAL_CANONICAL_SERIES_KEY],
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
                    "series_item_key": JDI_TOTAL_SERIES_ITEM_KEY,
                    "canonical_series_key": JDI_TOTAL_CANONICAL_SERIES_KEY,
                    "provider_series_id": "TOTAL",
                    "provider_group_key": JDI_PROVIDER_GROUP_KEY,
                    "ownership_mode": "grouped",
                    "owner_adapter_key": request.source_key,
                    "status": result.status,
                    "accepted_count": result.accepted_count,
                    "quarantined_count": result.quarantined_count,
                    "failed_count": result.failed_count,
                    "dynamic_series_count": len(
                        {
                            str(record.get("series_key", ""))
                            for record in records
                            if isinstance(record.get("series_key"), str)
                            and str(record.get("series_key", "")).strip() != ""
                            and str(record.get("series_key", "")) != JDI_TOTAL_CANONICAL_SERIES_KEY
                        }
                    ),
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
    "series_item_keys": (JDI_TOTAL_SERIES_ITEM_KEY,),
    "canonical_series_keys": (JDI_TOTAL_CANONICAL_SERIES_KEY,),
    "ownership_mode": "grouped",
    "cron_schedule": "0 7 * * *",
    "cadence_label": "daily",
    "builder": build_jdi_jail_population_source_workflow,
}
