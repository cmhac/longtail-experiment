"""EIA retail fuel prices source workflow adapter."""

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

EIA_RETAIL_FUEL_PRICES_SOURCE_KEY = "eia_retail_fuel_prices"
EIA_API_KEY_ENV = "EIA_API_KEY"


class EiaSeriesConfig(Protocol):
    """Typed view of one configured EIA product x geography series."""

    series_item_key: str
    provider_series_id: str
    provider_product_code: str
    provider_duoarea: str
    canonical_series_key: str
    metric_name: str
    dataset_description: str
    dataset_geographic_scope: str
    topic_tags: list[str]
    frequency: str


class EiaClient(Protocol):
    """Protocol for EIA observation fetch adapters."""

    def fetch_observations(
        self,
        *,
        api_key: str,
        product_code: str,
        duoarea: str,
        start_date: date | None,
    ) -> list[dict[str, Any]]:
        """Fetch EIA observation rows for one product and area."""


class _DefaultEiaClient:
    """HTTP adapter for fetching EIA weekly retail fuel observations."""

    def __init__(
        self,
        *,
        base_url: str = "https://api.eia.gov/v2/petroleum/pri/gnd/data",
        timeout: int = 30,
        page_size: int = 5000,
    ) -> None:
        self._base_url = base_url
        self._timeout = timeout
        self._page_size = page_size
        self._opener = build_opener()

    def fetch_observations(
        self,
        *,
        api_key: str,
        product_code: str,
        duoarea: str,
        start_date: date | None,
    ) -> list[dict[str, Any]]:
        offset = 0
        rows: list[dict[str, Any]] = []

        while True:
            params: list[tuple[str, str]] = [
                ("api_key", api_key),
                ("frequency", "weekly"),
                ("data[]", "value"),
                ("sort[0][column]", "period"),
                ("sort[0][direction]", "asc"),
                ("offset", str(offset)),
                ("length", str(self._page_size)),
                ("facets[duoarea][]", duoarea),
                ("facets[product][]", product_code),
            ]
            if start_date is not None:
                params.append(("start", start_date.isoformat()))

            url = f"{self._base_url}?{urlencode(params)}"
            try:
                with self._opener.open(url, timeout=self._timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except Exception as exc:  # pragma: no cover - network boundary
                raise RuntimeError("eia request failed") from exc

            response_payload = payload.get("response")
            if not isinstance(response_payload, dict):
                raise RuntimeError("eia response payload is invalid")

            page_rows = response_payload.get("data")
            if not isinstance(page_rows, list):
                raise RuntimeError("eia response data payload is invalid")

            rows.extend(row for row in page_rows if isinstance(row, dict))

            total = int(response_payload.get("total", len(rows)))
            if not page_rows or len(rows) >= total:
                break
            offset += self._page_size

        return rows


_EIA_PRODUCTS: tuple[dict[str, Any], ...] = (
    {
        "provider_product_code": "EPMR",
        "canonical_product_key": "RETAIL_GASOLINE",
        "series_item_suffix": "gasoline",
        "metric_name": "Regular All Formulations Retail Gasoline Prices",
        "dataset_description": (
            "Weekly EIA retail regular all formulations gasoline prices in dollars per gallon."
        ),
        "topic_tags": ["energy", "gasoline", "retail fuel prices", "eia"],
    },
    {
        "provider_product_code": "EPD2D",
        "canonical_product_key": "ONHIGHWAY_DIESEL",
        "series_item_suffix": "diesel",
        "metric_name": "On-Highway No. 2 Diesel Retail Prices",
        "dataset_description": "Weekly EIA on-highway no. 2 diesel prices in dollars per gallon.",
        "topic_tags": ["energy", "diesel", "retail fuel prices", "eia"],
    },
)

_EIA_GEOS: tuple[dict[str, str], ...] = (
    {
        "duoarea": "NUS",
        "series_item_suffix": "nus",
        "scope": "United States",
        "level_tag": "us",
    },
    {
        "duoarea": "R10",
        "series_item_suffix": "r10",
        "scope": "PADD Region 1",
        "level_tag": "region",
    },
    {
        "duoarea": "R20",
        "series_item_suffix": "r20",
        "scope": "PADD Region 2",
        "level_tag": "region",
    },
    {
        "duoarea": "R30",
        "series_item_suffix": "r30",
        "scope": "PADD Region 3",
        "level_tag": "region",
    },
    {
        "duoarea": "R40",
        "series_item_suffix": "r40",
        "scope": "PADD Region 4",
        "level_tag": "region",
    },
    {
        "duoarea": "R50",
        "series_item_suffix": "r50",
        "scope": "PADD Region 5",
        "level_tag": "region",
    },
    {
        "duoarea": "SCA",
        "series_item_suffix": "sca",
        "scope": "California",
        "level_tag": "state",
    },
    {
        "duoarea": "SCO",
        "series_item_suffix": "sco",
        "scope": "Colorado",
        "level_tag": "state",
    },
    {
        "duoarea": "SFL",
        "series_item_suffix": "sfl",
        "scope": "Florida",
        "level_tag": "state",
    },
    {
        "duoarea": "SMA",
        "series_item_suffix": "sma",
        "scope": "Massachusetts",
        "level_tag": "state",
    },
    {
        "duoarea": "SMN",
        "series_item_suffix": "smn",
        "scope": "Minnesota",
        "level_tag": "state",
    },
    {
        "duoarea": "SNY",
        "series_item_suffix": "sny",
        "scope": "New York",
        "level_tag": "state",
    },
    {
        "duoarea": "SOH",
        "series_item_suffix": "soh",
        "scope": "Ohio",
        "level_tag": "state",
    },
    {
        "duoarea": "STX",
        "series_item_suffix": "stx",
        "scope": "Texas",
        "level_tag": "state",
    },
    {
        "duoarea": "SWA",
        "series_item_suffix": "swa",
        "scope": "Washington",
        "level_tag": "state",
    },
)

_UNAVAILABLE_DIESEL_STATE_DUOAREAS: set[str] = {
    "SCO",
    "SFL",
    "SMA",
    "SMN",
    "SNY",
    "SOH",
    "STX",
    "SWA",
}


def _build_series_configs() -> tuple[dict[str, Any], ...]:
    configs: list[dict[str, Any]] = []
    for product in _EIA_PRODUCTS:
        for geography in _EIA_GEOS:
            if (
                product["provider_product_code"] == "EPD2D"
                and geography["duoarea"] in _UNAVAILABLE_DIESEL_STATE_DUOAREAS
            ):
                continue
            configs.append(
                {
                    "series_item_key": (
                        f"eia_{product['series_item_suffix']}_{geography['series_item_suffix']}"
                    ),
                    "provider_series_id": (
                        f"{product['provider_product_code']}.{geography['duoarea']}"
                    ),
                    "provider_product_code": product["provider_product_code"],
                    "provider_duoarea": geography["duoarea"],
                    "canonical_series_key": (
                        f"ENERGY.US.{product['canonical_product_key']}.{geography['duoarea']}"
                    ),
                    "metric_name": f"{product['metric_name']} - {geography['scope']}",
                    "dataset_description": (
                        f"{product['dataset_description']} Geography: {geography['scope']}"
                    ),
                    "dataset_geographic_scope": geography["scope"],
                    "topic_tags": [*product["topic_tags"], geography["level_tag"]],
                    "frequency": "weekly",
                }
            )
    return tuple(configs)


SERIES_CONFIGS: tuple[dict[str, Any], ...] = _build_series_configs()


def _map_records(
    *,
    rows: Sequence[dict[str, Any]],
    series_config: dict[str, Any],
) -> list[dict[str, object]]:
    mapped: list[dict[str, object]] = []
    now_iso = datetime.now(tz=UTC).isoformat()
    for row in rows:
        value = row.get("value")
        period = row.get("period")
        if value is None or period is None:
            continue

        value_str = str(value).strip()
        if not value_str:
            continue

        reported_at = row.get("updated") or row.get("last-updated") or now_iso
        mapped.append(
            {
                "source_name": "EIA",
                "source_type": "external",
                "series_key": series_config["canonical_series_key"],
                "metric_name": series_config["metric_name"],
                "dataset_title": series_config["metric_name"],
                "dataset_description": series_config["dataset_description"],
                "dataset_geographic_scope": series_config["dataset_geographic_scope"],
                "topic_tags": series_config["topic_tags"],
                "frequency": series_config["frequency"],
                "date": str(period),
                "reported_at": str(reported_at),
                "value": value_str,
                "unit": str(row.get("units") or "Dollars per Gallon"),
                "attributes": {
                    "provider_series_id": series_config["provider_series_id"],
                    "provider_duoarea": str(
                        row.get("duoarea") or series_config["provider_duoarea"]
                    ),
                    "provider_area_name": str(row.get("area-name") or ""),
                    "provider_product_code": str(
                        row.get("product") or series_config["provider_product_code"]
                    ),
                    "provider_product_name": str(row.get("product-name") or ""),
                },
            }
        )
    return mapped


def build_eia_retail_fuel_prices_source_workflow(
    runner: SourceIngestRunner,
    *,
    observation_repository: ObservationCheckpointRepository,
    client: EiaClient | None = None,
    schedule_policy: SourceSchedulePolicy | None = None,
) -> SourceWorkflowRegistration:
    """Build workflow registration for eia_retail_fuel_prices."""
    eia_client = client or _DefaultEiaClient()

    def _handler(request: SourceWorkflowRequest) -> SourceWorkflowResult:
        passthrough_records = request.run_context.get("records")
        if passthrough_records is not None:
            if not isinstance(passthrough_records, list):
                raise ValueError("run_context.records must be a list")
            return runner.run_records(request=request, records=passthrough_records)

        run_context_key = request.run_context.get("api_key")
        api_key = (
            run_context_key
            if isinstance(run_context_key, str) and run_context_key.strip()
            else None
        )
        if api_key is None:
            env_key = os.getenv(EIA_API_KEY_ENV, "").strip()
            api_key = env_key or None
        if api_key is None:
            return SourceWorkflowResult(
                source_key=request.source_key,
                status="failure",
                accepted_count=0,
                quarantined_count=0,
                failed_count=0,
                outcome_reason_code="missing_credentials",
                message="EIA_API_KEY is required for eia_retail_fuel_prices source",
                series_outcomes=[],
            )

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
                series_key=series_config["canonical_series_key"],
            )
            start_date = latest + timedelta(days=1) if latest is not None else None

            try:
                raw_rows = eia_client.fetch_observations(
                    api_key=api_key,
                    product_code=series_config["provider_product_code"],
                    duoarea=series_config["provider_duoarea"],
                    start_date=start_date,
                )
            except Exception as exc:
                failed_count += 1
                series_outcomes.append(
                    {
                        "series_item_key": series_config["series_item_key"],
                        "canonical_series_key": series_config["canonical_series_key"],
                        "provider_series_id": series_config["provider_series_id"],
                        "provider_group_key": "eia",
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
            )
            accepted_count += result.accepted_count
            quarantined_count += result.quarantined_count
            failed_count += result.failed_count
            series_outcomes.append(
                {
                    "series_item_key": series_config["series_item_key"],
                    "canonical_series_key": series_config["canonical_series_key"],
                    "provider_series_id": series_config["provider_series_id"],
                    "provider_group_key": "eia",
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
            message = "all configured EIA series failed provider retrieval"
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
        workflow_id="wf-eia-retail-fuel-prices",
        source_key=EIA_RETAIL_FUEL_PRICES_SOURCE_KEY,
        owner="pipeline",
        supported_trigger_modes={"scheduled", "on_demand"},
        handler=_handler,
        schedule_policy=schedule_policy,
    )


SOURCE_SPEC: dict[str, Any] = {
    "source_key": EIA_RETAIL_FUEL_PRICES_SOURCE_KEY,
    "provider_group_key": "eia",
    "series_item_keys": tuple(config["series_item_key"] for config in SERIES_CONFIGS),
    "canonical_series_keys": tuple(config["canonical_series_key"] for config in SERIES_CONFIGS),
    "ownership_mode": "grouped",
    "cron_schedule": "0 9 * * 1",
    "cadence_label": "weekly",
    "builder": build_eia_retail_fuel_prices_source_workflow,
}
