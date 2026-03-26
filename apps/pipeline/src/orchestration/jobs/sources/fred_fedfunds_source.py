"""FRED FEDFUNDS source workflow adapter."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta
from typing import Any, Protocol
from urllib.parse import urlencode
from urllib.request import build_opener

from ..source_assets.discovery import ObservationCheckpointRepository
from ..source_ingest_runner import SourceIngestRunner
from ..source_schedule_policy import SourceSchedulePolicy
from ..workflow_registry import SourceWorkflowRegistration
from ..workflow_request import SourceWorkflowRequest
from ..workflow_result import SourceWorkflowResult

FRED_FEDFUNDS_SOURCE_KEY = "fred_fedfunds"
FRED_FEDFUNDS_SERIES_ID = "FEDFUNDS"
FRED_FEDFUNDS_CANONICAL_SERIES = "INT.US.FEDFUNDS"
FRED_GASREGW_SERIES_ID = "GASREGW"
FRED_GASREGW_CANONICAL_SERIES = "ENERGY.US.GASREGW"
FRED_API_KEY_ENV = "FRED_API_KEY"


class FredSeriesConfig(Protocol):
    """Typed view of per-series FRED adapter configuration."""

    series_item_key: str
    provider_series_id: str
    canonical_series_key: str
    metric_name: str
    dataset_description: str
    dataset_geographic_scope: str
    topic_tags: list[str]


FRED_SERIES_CONFIGS: tuple[dict[str, Any], ...] = (
    {
        "series_item_key": "fred_fedfunds",
        "provider_series_id": FRED_FEDFUNDS_SERIES_ID,
        "canonical_series_key": FRED_FEDFUNDS_CANONICAL_SERIES,
        "metric_name": "Effective Federal Funds Rate",
        "dataset_description": "Federal funds effective interest rate published by FRED.",
        "dataset_geographic_scope": "United States",
        "topic_tags": ["interest rates", "monetary policy", "federal reserve"],
    },
    {
        "series_item_key": "fred_gasregw",
        "provider_series_id": FRED_GASREGW_SERIES_ID,
        "canonical_series_key": FRED_GASREGW_CANONICAL_SERIES,
        "metric_name": "US Regular Gas Price",
        "dataset_description": "Average retail regular gasoline price from FRED.",
        "dataset_geographic_scope": "United States",
        "topic_tags": ["energy", "gasoline", "consumer prices"],
    },
)


class FredClient(Protocol):
    """Protocol for FRED observation fetch adapters."""

    def fetch_observations(
        self,
        *,
        api_key: str,
        series_id: str,
        start_date: date | None,
    ) -> list[dict[str, Any]]:
        """Fetch FRED observation rows for one series."""


class _DefaultFredClient:
    """HTTP adapter for fetching FRED observations."""

    def __init__(self, *, base_url: str = "https://api.stlouisfed.org", timeout: int = 15) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._opener = build_opener()

    def fetch_observations(
        self,
        *,
        api_key: str,
        series_id: str,
        start_date: date | None,
    ) -> list[dict[str, Any]]:
        query: dict[str, str] = {
            "api_key": api_key,
            "file_type": "json",
            "sort_order": "asc",
            "series_id": series_id,
        }
        if start_date is not None:
            query["observation_start"] = start_date.isoformat()

        url = f"{self._base_url}/fred/series/observations?{urlencode(query)}"
        try:
            with self._opener.open(url, timeout=self._timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - network boundary
            raise RuntimeError("fred request failed") from exc

        observations = payload.get("observations", [])
        if not isinstance(observations, list):
            raise RuntimeError("fred response observations payload is invalid")
        return [row for row in observations if isinstance(row, dict)]


def _map_fred_records(
    *,
    rows: Sequence[dict[str, Any]],
    series_config: dict[str, Any],
) -> list[dict[str, object]]:
    mapped: list[dict[str, object]] = []
    now_iso = datetime.now(tz=UTC).isoformat()
    metric_name = series_config["metric_name"]
    for row in rows:
        mapped.append(
            {
                "source_name": "FRED",
                "source_type": "external",
                "series_key": series_config["canonical_series_key"],
                "metric_name": metric_name,
                "dataset_title": metric_name,
                "dataset_description": series_config["dataset_description"],
                "dataset_geographic_scope": series_config["dataset_geographic_scope"],
                "topic_tags": [
                    tag.strip()
                    for tag in series_config["topic_tags"]
                    if isinstance(tag, str) and tag.strip()
                ],
                "date": str(row.get("date", "")),
                "reported_at": str(row.get("realtime_end") or row.get("realtime_start") or now_iso),
                "value": str(row.get("value", "")),
                "attributes": {
                    "provider_series_id": series_config["provider_series_id"],
                },
            }
        )
    return mapped


def build_fred_fedfunds_source_workflow(
    runner: SourceIngestRunner,
    *,
    observation_repository: ObservationCheckpointRepository,
    client: FredClient | None = None,
    schedule_policy: SourceSchedulePolicy | None = None,
) -> SourceWorkflowRegistration:
    """Build workflow registration for FRED FEDFUNDS ingestion."""
    fred_client = client or _DefaultFredClient()

    def _handler(request: SourceWorkflowRequest) -> SourceWorkflowResult:
        records = request.run_context.get("records")
        if records is not None:
            if not isinstance(records, list):
                raise ValueError("run_context.records must be a list")
            return runner.run_records(request=request, records=records)

        run_context_key = request.run_context.get("api_key")
        api_key = (
            run_context_key
            if isinstance(run_context_key, str) and run_context_key.strip()
            else None
        )
        if api_key is None:
            env_key = os.getenv(FRED_API_KEY_ENV, "").strip()
            api_key = env_key or None
        if api_key is None:
            raise OSError("FRED_API_KEY is required for fred_fedfunds source but is not set")

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

        for series_config in FRED_SERIES_CONFIGS:
            if (
                requested_series_items is not None
                and series_config["series_item_key"] not in requested_series_items
            ):
                continue
            canonical_series_key = series_config["canonical_series_key"]
            provider_series_id = series_config["provider_series_id"]
            latest = observation_repository.read_latest_observed_on(
                series_key=canonical_series_key,
            )
            start_date = latest + timedelta(days=1) if latest is not None else None

            try:
                raw_rows = fred_client.fetch_observations(
                    api_key=api_key,
                    series_id=provider_series_id,
                    start_date=start_date,
                )
            except Exception as exc:
                failed_count += 1
                series_outcomes.append(
                    {
                        "series_item_key": series_config["series_item_key"],
                        "canonical_series_key": canonical_series_key,
                        "provider_series_id": provider_series_id,
                        "provider_group_key": "fred",
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

            series_result = runner.run_records(
                request=request,
                records=_map_fred_records(
                    rows=raw_rows,
                    series_config=series_config,
                ),
            )
            accepted_count += series_result.accepted_count
            quarantined_count += series_result.quarantined_count
            failed_count += series_result.failed_count
            series_outcomes.append(
                {
                    "series_item_key": series_config["series_item_key"],
                    "canonical_series_key": canonical_series_key,
                    "provider_series_id": provider_series_id,
                    "provider_group_key": "fred",
                    "ownership_mode": "grouped",
                    "owner_adapter_key": request.source_key,
                    "status": series_result.status,
                    "accepted_count": series_result.accepted_count,
                    "quarantined_count": series_result.quarantined_count,
                    "failed_count": series_result.failed_count,
                }
            )

        if failed_count > 0 and accepted_count == 0 and quarantined_count == 0:
            status = "failure"
            outcome_reason = "provider_request_failed"
            message = "all configured FRED series failed provider retrieval"
        elif failed_count > 0 or quarantined_count > 0:
            status = "partial_success"
            outcome_reason = None
            message = None
        else:
            status = "success"
            outcome_reason = None
            message = None

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
        workflow_id="wf-fred-fedfunds",
        source_key=FRED_FEDFUNDS_SOURCE_KEY,
        owner="pipeline",
        supported_trigger_modes={"scheduled", "on_demand"},
        handler=_handler,
        schedule_policy=schedule_policy,
    )


SOURCE_SPEC: dict[str, Any] = {
    "source_key": FRED_FEDFUNDS_SOURCE_KEY,
    "provider_group_key": "fred",
    "series_item_keys": ("fred_fedfunds", "fred_gasregw"),
    "canonical_series_keys": (FRED_FEDFUNDS_CANONICAL_SERIES, FRED_GASREGW_CANONICAL_SERIES),
    "ownership_mode": "grouped",
    "cron_schedule": "0 0 * * *",
    "cadence_label": "daily",
    "builder": build_fred_fedfunds_source_workflow,
}
