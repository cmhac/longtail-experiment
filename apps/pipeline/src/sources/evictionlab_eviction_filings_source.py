"""
Eviction Lab eviction filings source workflow adapter.

Ingests monthly eviction filing counts from the Eviction Lab (Princeton
University) for 51 US cities and states.  Each site is published as a separate
CSV file containing sub-geography rows (Census Tract / ZIP Code) that are
aggregated to site-level totals before being emitted as canonical observations.
"""

from __future__ import annotations

import csv
import io
from calendar import monthrange
from collections import defaultdict
from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta
from typing import Any, Protocol
from urllib.request import build_opener

from src.orchestration.jobs.source_assets.discovery import ObservationCheckpointRepository
from src.orchestration.jobs.source_ingest_runner import SourceIngestRunner
from src.orchestration.jobs.source_schedule_policy import SourceSchedulePolicy
from src.orchestration.jobs.workflow_registry import SourceWorkflowRegistration
from src.orchestration.jobs.workflow_request import SourceWorkflowRequest
from src.orchestration.jobs.workflow_result import SourceWorkflowResult

EVICTIONLAB_EVICTION_FILINGS_SOURCE_KEY = "evictionlab_eviction_filings"
EVICTIONLAB_PROVIDER_GROUP_KEY = "evictionlab"
EVICTIONLAB_SOURCE_NAME = "EVICTIONLAB"
EVICTIONLAB_SOURCE_TITLE = "Eviction Lab Eviction Filings"
EVICTIONLAB_SOURCE_DESCRIPTION = (
    "Monthly eviction filing counts aggregated to the site level from "
    "Eviction Lab (Princeton University) sub-geography CSV data for "
    "51 US cities and states."
)

# ---------------------------------------------------------------------------
# Site catalogue — each entry defines one series
# ---------------------------------------------------------------------------

_SITES: tuple[dict[str, str], ...] = (
    {"slug": "albuquerque", "name": "Albuquerque", "scope": "New Mexico"},
    {"slug": "atlanta", "name": "Atlanta", "scope": "Georgia"},
    {"slug": "austin", "name": "Austin", "scope": "Texas"},
    {"slug": "boston", "name": "Boston", "scope": "Massachusetts"},
    {"slug": "bridgeport", "name": "Bridgeport", "scope": "Connecticut"},
    {"slug": "charleston", "name": "Charleston", "scope": "South Carolina"},
    {"slug": "cincinnati", "name": "Cincinnati", "scope": "Ohio"},
    {"slug": "cleveland", "name": "Cleveland", "scope": "Ohio"},
    {"slug": "columbus", "name": "Columbus", "scope": "Ohio"},
    {"slug": "connecticut", "name": "Connecticut", "scope": "Connecticut"},
    {"slug": "dallas", "name": "Dallas", "scope": "Texas"},
    {"slug": "delaware", "name": "Delaware", "scope": "Delaware"},
    {"slug": "eugene", "name": "Eugene", "scope": "Oregon"},
    {"slug": "fortlauderdale", "name": "Fort Lauderdale", "scope": "Florida"},
    {"slug": "fortworth", "name": "Fort Worth", "scope": "Texas"},
    {"slug": "gainesville", "name": "Gainesville", "scope": "Florida"},
    {"slug": "greenville", "name": "Greenville", "scope": "South Carolina"},
    {"slug": "hartford", "name": "Hartford", "scope": "Connecticut"},
    {"slug": "houston", "name": "Houston", "scope": "Texas"},
    {"slug": "indiana", "name": "Indiana", "scope": "Indiana"},
    {"slug": "indianapolis", "name": "Indianapolis", "scope": "Indiana"},
    {"slug": "jacksonville", "name": "Jacksonville", "scope": "Florida"},
    {"slug": "kansascity", "name": "Kansas City", "scope": "Missouri"},
    {"slug": "lasvegas", "name": "Las Vegas", "scope": "Nevada"},
    {"slug": "miami", "name": "Miami", "scope": "Florida"},
    {"slug": "memphis", "name": "Memphis", "scope": "Tennessee"},
    {"slug": "milwaukee", "name": "Milwaukee", "scope": "Wisconsin"},
    {"slug": "minneapolis", "name": "Minneapolis", "scope": "Minnesota"},
    {"slug": "minnesota", "name": "Minnesota", "scope": "Minnesota"},
    {"slug": "missouri", "name": "Missouri", "scope": "Missouri"},
    {"slug": "nashville", "name": "Nashville", "scope": "Tennessee"},
    {"slug": "newmexico", "name": "New Mexico", "scope": "New Mexico"},
    {"slug": "neworleans", "name": "New Orleans", "scope": "Louisiana"},
    {"slug": "newyork", "name": "New York", "scope": "New York"},
    {"slug": "pennsylvania", "name": "Pennsylvania", "scope": "Pennsylvania"},
    {"slug": "philadelphia", "name": "Philadelphia", "scope": "Pennsylvania"},
    {"slug": "phoenix", "name": "Phoenix", "scope": "Arizona"},
    {"slug": "pittsburgh", "name": "Pittsburgh", "scope": "Pennsylvania"},
    {"slug": "portland", "name": "Portland", "scope": "Oregon"},
    {"slug": "providence", "name": "Providence", "scope": "Rhode Island"},
    {"slug": "rhode_island", "name": "Rhode Island", "scope": "Rhode Island"},
    {"slug": "richmond", "name": "Richmond", "scope": "Virginia"},
    {"slug": "southbend", "name": "South Bend", "scope": "Indiana"},
    {"slug": "southwest", "name": "Southwest Oregon", "scope": "Oregon"},
    {"slug": "stlouis", "name": "St. Louis", "scope": "Missouri"},
    {"slug": "tacoma", "name": "Tacoma", "scope": "Washington"},
    {"slug": "tampa", "name": "Tampa", "scope": "Florida"},
    {"slug": "virginia", "name": "Virginia", "scope": "Virginia"},
    {"slug": "palmbeach", "name": "West Palm Beach", "scope": "Florida"},
    {"slug": "wilmington", "name": "Wilmington", "scope": "Delaware"},
    {"slug": "wisconsin", "name": "Wisconsin", "scope": "Wisconsin"},
)


def _canonical_key_suffix(slug: str) -> str:
    """Derive the uppercase canonical key suffix from a site slug."""
    return slug.upper()


def _build_series_configs() -> tuple[dict[str, Any], ...]:
    """Generate one series config per site."""
    configs: list[dict[str, Any]] = []
    for site in _SITES:
        suffix = _canonical_key_suffix(site["slug"])
        configs.append(
            {
                "series_item_key": f"eviction_filings_{site['slug']}",
                "provider_series_id": site["slug"],
                "canonical_series_key": f"HOUSING.US.EVICTION_FILINGS.{suffix}",
                "metric_name": f"Eviction Filings - {site['name']}",
                "dataset_description": (
                    f"Monthly eviction filing counts for {site['name']} "
                    f"aggregated from Census Tract / ZIP Code level data "
                    f"published by Eviction Lab (Princeton University)."
                ),
                "dataset_geographic_scope": site["scope"],
                "topic_tags": ["housing", "eviction", "legal", "eviction lab"],
                "frequency": "monthly",
                "csv_slug": site["slug"],
            }
        )
    return tuple(configs)


SERIES_CONFIGS: tuple[dict[str, Any], ...] = _build_series_configs()

# ---------------------------------------------------------------------------
# Client protocol and default HTTP implementation
# ---------------------------------------------------------------------------

_CSV_URL_TEMPLATE = "https://evictionlab.org/uploads/{slug}_monthly_2020_2021.csv"


class EvictionLabClient(Protocol):
    """Protocol for Eviction Lab CSV fetch adapters."""

    def fetch_monthly_csv(
        self,
        *,
        slug: str,
    ) -> list[dict[str, str]]:
        """Return parsed CSV rows for one site's monthly data."""
        raise NotImplementedError


class _DefaultEvictionLabClient:
    """HTTP adapter that downloads and parses Eviction Lab monthly CSVs."""

    def __init__(
        self,
        *,
        base_url_template: str = _CSV_URL_TEMPLATE,
        timeout: int = 60,
    ) -> None:
        self._base_url_template = base_url_template
        self._timeout = timeout
        self._opener = build_opener()

    def fetch_monthly_csv(
        self,
        *,
        slug: str,
    ) -> list[dict[str, str]]:
        url = self._base_url_template.format(slug=slug)
        try:
            with self._opener.open(url, timeout=self._timeout) as response:
                raw = response.read().decode("utf-8")
        except Exception as exc:  # pragma: no cover - network boundary
            raise RuntimeError(f"evictionlab csv download failed for {slug}: {exc}") from exc

        reader = csv.DictReader(io.StringIO(raw))
        return [dict(row) for row in reader]


# ---------------------------------------------------------------------------
# Aggregation and record mapping
# ---------------------------------------------------------------------------


_MONTH_YEAR_PARTS = 2
_MAX_MONTH = 12
_MIN_YEAR = 2000


def _parse_month_to_iso(month_str: str) -> str | None:
    """
    Convert MM/YYYY to ISO date string (YYYY-MM-01).

    Returns *None* if the value cannot be parsed.
    """
    parts = month_str.strip().split("/")
    if len(parts) != _MONTH_YEAR_PARTS:
        return None
    try:
        mm = int(parts[0])
        yyyy = int(parts[1])
    except ValueError:
        return None
    if not (1 <= mm <= _MAX_MONTH) or yyyy < _MIN_YEAR:
        return None
    return f"{yyyy:04d}-{mm:02d}-01"


def _is_incomplete_month(*, iso_date: str, last_updated: str) -> bool:
    """Return True when month appears to be a partial in-progress period."""
    if not last_updated:
        return False

    try:
        observed_month = date.fromisoformat(iso_date)
        updated_on = date.fromisoformat(last_updated)
    except ValueError:
        return False

    if observed_month.year != updated_on.year or observed_month.month != updated_on.month:
        return False

    last_day = monthrange(updated_on.year, updated_on.month)[1]
    return updated_on.day < last_day


def _aggregate_site_monthly(
    rows: Sequence[dict[str, str]],
    *,
    start_date: date | None,
) -> list[dict[str, Any]]:
    """
    Aggregate sub-geography rows to site-level monthly totals.

    Each output dict contains:
      date          – ISO date (first of month)
      filings       – sum of ``filings_2020`` across GEOIDs
      filings_avg   – sum of ``filings_avg``
      filings_avg_prepandemic – sum of ``filings_avg_prepandemic_baseline``
      last_updated  – max ``last_updated`` value across rows in the month
    """
    month_filings: dict[str, float] = defaultdict(float)
    month_filings_avg: dict[str, float] = defaultdict(float)
    month_filings_avg_pre: dict[str, float] = defaultdict(float)
    month_last_updated: dict[str, str] = defaultdict(str)

    for row in rows:
        iso_date = _parse_month_to_iso(row.get("month", ""))
        if iso_date is None:
            continue

        if start_date is not None and iso_date < start_date.isoformat():
            continue

        filings_raw = row.get("filings_2020", "").strip()
        filings_avg_raw = row.get("filings_avg", "").strip()
        filings_avg_pre_raw = row.get("filings_avg_prepandemic_baseline", "").strip()
        last_updated = row.get("last_updated", "").strip()

        try:
            filings_val = float(filings_raw) if filings_raw else 0.0
        except ValueError:
            filings_val = 0.0

        try:
            filings_avg_val = float(filings_avg_raw) if filings_avg_raw else 0.0
        except ValueError:
            filings_avg_val = 0.0

        try:
            filings_avg_pre_val = float(filings_avg_pre_raw) if filings_avg_pre_raw else 0.0
        except ValueError:
            filings_avg_pre_val = 0.0

        month_filings[iso_date] += filings_val
        month_filings_avg[iso_date] += filings_avg_val
        month_filings_avg_pre[iso_date] += filings_avg_pre_val
        month_last_updated[iso_date] = max(month_last_updated[iso_date], last_updated)

    result: list[dict[str, Any]] = []
    for iso_date in sorted(month_filings):
        filings_total = month_filings[iso_date]
        last_updated = month_last_updated[iso_date]
        if _is_incomplete_month(iso_date=iso_date, last_updated=last_updated):
            continue
        if filings_total == 0.0:
            continue
        result.append(
            {
                "date": iso_date,
                "filings": filings_total,
                "filings_avg": month_filings_avg[iso_date],
                "filings_avg_prepandemic": month_filings_avg_pre[iso_date],
                "last_updated": last_updated,
            }
        )
    return result


def _map_records(
    *,
    aggregated_rows: Sequence[dict[str, Any]],
    series_config: dict[str, Any],
) -> list[dict[str, object]]:
    """Map aggregated site-level rows to canonical observation dicts."""
    mapped: list[dict[str, object]] = []
    now_iso = datetime.now(tz=UTC).isoformat()

    for row in aggregated_rows:
        value = row.get("filings")
        obs_date = row.get("date")
        if value is None or obs_date is None:
            continue

        value_str = str(int(value)) if float(value) == int(value) else str(value)

        last_updated = row.get("last_updated", "")
        reported_at = f"{last_updated}T00:00:00+00:00" if last_updated else now_iso

        mapped.append(
            {
                "source_name": EVICTIONLAB_SOURCE_NAME,
                "source_key": EVICTIONLAB_PROVIDER_GROUP_KEY,
                "source_title": EVICTIONLAB_SOURCE_TITLE,
                "source_description": EVICTIONLAB_SOURCE_DESCRIPTION,
                "source_type": "external",
                "series_key": series_config["canonical_series_key"],
                "metric_name": series_config["metric_name"],
                "dataset_title": series_config["metric_name"],
                "dataset_description": series_config["dataset_description"],
                "dataset_geographic_scope": series_config["dataset_geographic_scope"],
                "topic_tags": series_config["topic_tags"],
                "frequency": series_config["frequency"],
                "date": str(obs_date),
                "reported_at": str(reported_at),
                "value": value_str,
                "unit": "filings",
                "unit_type": "number",
                "attributes": {
                    "provider_series_id": series_config["provider_series_id"],
                    "filings_avg": str(row.get("filings_avg", "")),
                    "filings_avg_prepandemic": str(row.get("filings_avg_prepandemic", "")),
                },
            }
        )
    return mapped


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


def build_evictionlab_eviction_filings_source_workflow(
    runner: SourceIngestRunner,
    *,
    observation_repository: ObservationCheckpointRepository,
    client: EvictionLabClient | None = None,
    schedule_policy: SourceSchedulePolicy | None = None,
) -> SourceWorkflowRegistration:
    """Build workflow registration for evictionlab_eviction_filings."""
    eviction_client = client or _DefaultEvictionLabClient()

    def _handler(request: SourceWorkflowRequest) -> SourceWorkflowResult:
        runner.sync_source_metadata(
            source_key=EVICTIONLAB_PROVIDER_GROUP_KEY,
            source_name=EVICTIONLAB_SOURCE_NAME,
            source_title=EVICTIONLAB_SOURCE_TITLE,
            source_description=EVICTIONLAB_SOURCE_DESCRIPTION,
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
        cadence_decisions: list[dict[str, object]] = []

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
                series_key=series_config["canonical_series_key"],
            )
            start_date = latest + timedelta(days=1) if latest is not None else None

            try:
                raw_rows = eviction_client.fetch_monthly_csv(
                    slug=series_config["csv_slug"],
                )
            except Exception as exc:
                failed_count += 1
                series_outcomes.append(
                    {
                        "series_item_key": series_config["series_item_key"],
                        "canonical_series_key": series_config["canonical_series_key"],
                        "provider_series_id": series_config["provider_series_id"],
                        "provider_group_key": EVICTIONLAB_PROVIDER_GROUP_KEY,
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

            aggregated = _aggregate_site_monthly(raw_rows, start_date=start_date)
            records = _map_records(
                aggregated_rows=aggregated,
                series_config=series_config,
            )

            result = runner.run_records(
                request=request,
                records=records,
                fallback_series_keys=[series_config["canonical_series_key"]],
            )

            cadence_decision = next(
                (
                    decision
                    for decision in result.cadence_decisions
                    if decision.get("series_key") == series_config["canonical_series_key"]
                ),
                None,
            )
            if isinstance(cadence_decision, dict):
                cadence_decisions.append(dict(cadence_decision))

            accepted_count += result.accepted_count
            quarantined_count += result.quarantined_count
            failed_count += result.failed_count
            series_outcomes.append(
                {
                    "series_item_key": series_config["series_item_key"],
                    "canonical_series_key": series_config["canonical_series_key"],
                    "provider_series_id": series_config["provider_series_id"],
                    "provider_group_key": EVICTIONLAB_PROVIDER_GROUP_KEY,
                    "ownership_mode": "grouped",
                    "owner_adapter_key": request.source_key,
                    "status": result.status,
                    "accepted_count": result.accepted_count,
                    "quarantined_count": result.quarantined_count,
                    "failed_count": result.failed_count,
                    "cadence_decision": cadence_decision,
                }
            )

        status = "success"
        outcome_reason: str | None = None
        message: str | None = None
        if failed_count > 0 and accepted_count == 0 and quarantined_count == 0:
            status = "failure"
            outcome_reason = "provider_request_failed"
            message = "all configured Eviction Lab sites failed provider retrieval"
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
            cadence_decisions=cadence_decisions,
        )

    return SourceWorkflowRegistration(
        workflow_id="wf-evictionlab-eviction-filings",
        source_key=EVICTIONLAB_EVICTION_FILINGS_SOURCE_KEY,
        owner="pipeline",
        supported_trigger_modes={"scheduled", "on_demand"},
        handler=_handler,
        schedule_policy=schedule_policy,
    )


# ---------------------------------------------------------------------------
# SOURCE_SPEC — discovered automatically by the pipeline registration system
# ---------------------------------------------------------------------------

SOURCE_SPEC: dict[str, Any] = {
    "source_key": EVICTIONLAB_EVICTION_FILINGS_SOURCE_KEY,
    "provider_group_key": EVICTIONLAB_PROVIDER_GROUP_KEY,
    "title": EVICTIONLAB_SOURCE_TITLE,
    "description": EVICTIONLAB_SOURCE_DESCRIPTION,
    "series_item_keys": tuple(config["series_item_key"] for config in SERIES_CONFIGS),
    "canonical_series_keys": tuple(config["canonical_series_key"] for config in SERIES_CONFIGS),
    "ownership_mode": "grouped",
    "cron_schedule": "0 0 2 * *",
    "cadence_label": "monthly",
    "builder": build_evictionlab_eviction_filings_source_workflow,
}
