"""FRED FEDFUNDS source workflow adapter."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta
from typing import Any, Protocol
from urllib.parse import urlencode
from urllib.request import urlopen

from ..source_ingest_runner import SourceIngestRunner
from ..source_schedule_policy import SourceSchedulePolicy
from ..workflow_registry import SourceWorkflowRegistration
from ..workflow_request import SourceWorkflowRequest
from ..workflow_result import SourceWorkflowResult

FRED_FEDFUNDS_SOURCE_KEY = "fred_fedfunds"
FRED_FEDFUNDS_SERIES_ID = "FEDFUNDS"
FRED_FEDFUNDS_CANONICAL_SERIES = "INT.US.FEDFUNDS"
FRED_API_KEY_ENV = "FRED_API_KEY"


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
            with urlopen(url, timeout=self._timeout) as response:  # noqa: S310 - trusted FRED endpoint
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - network boundary
            raise RuntimeError("fred request failed") from exc

        observations = payload.get("observations", [])
        if not isinstance(observations, list):
            raise RuntimeError("fred response observations payload is invalid")
        return [row for row in observations if isinstance(row, dict)]


class ObservationCheckpointRepository(Protocol):
    """Protocol for reading latest persisted canonical observation dates."""

    def read_latest_observed_on(self, *, series_key: str) -> date | None:
        """Return latest persisted observation date for one canonical series."""


def _map_fred_records(rows: Sequence[dict[str, Any]]) -> list[dict[str, object]]:
    mapped: list[dict[str, object]] = []
    now_iso = datetime.now(tz=UTC).isoformat()
    for row in rows:
        mapped.append(
            {
                "source_name": "FRED",
                "source_type": "external",
                "series_key": FRED_FEDFUNDS_CANONICAL_SERIES,
                "metric_name": "Effective Federal Funds Rate",
                "frequency": "daily",
                "date": str(row.get("date", "")),
                "reported_at": str(row.get("realtime_end") or row.get("realtime_start") or now_iso),
                "value": str(row.get("value", "")),
                "attributes": {
                    "provider_series_id": FRED_FEDFUNDS_SERIES_ID,
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
            return SourceWorkflowResult(
                source_key=request.source_key,
                status="failure",
                failed_count=1,
                outcome_reason_code="missing_credentials",
                message="FRED_API_KEY is required for fred_fedfunds source",
            )

        latest = observation_repository.read_latest_observed_on(
            series_key=FRED_FEDFUNDS_CANONICAL_SERIES,
        )
        start_date = latest + timedelta(days=1) if latest is not None else None

        try:
            raw_rows = fred_client.fetch_observations(
                api_key=api_key,
                series_id=FRED_FEDFUNDS_SERIES_ID,
                start_date=start_date,
            )
        except Exception as exc:
            return SourceWorkflowResult(
                source_key=request.source_key,
                status="failure",
                failed_count=1,
                outcome_reason_code="provider_request_failed",
                message=str(exc),
            )

        return runner.run_records(request=request, records=_map_fred_records(raw_rows))

    return SourceWorkflowRegistration(
        workflow_id="wf-fred-fedfunds",
        source_key=FRED_FEDFUNDS_SOURCE_KEY,
        owner="pipeline",
        supported_trigger_modes={"scheduled", "on_demand"},
        handler=_handler,
        schedule_policy=schedule_policy,
    )
