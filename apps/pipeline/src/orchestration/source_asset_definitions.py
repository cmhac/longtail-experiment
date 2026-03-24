"""Dagster asset definitions for source-level visibility in Dagit."""

from __future__ import annotations

from typing import Any

from dagster import asset

from .jobs.source_assets.discovery import scan_adapter_modules
from .schedules.source_asset_schedules import SOURCE_CADENCE_DEFINITIONS


def _run_single_source(
    *,
    context,
    source_key: str,
) -> dict[str, Any]:
    """Execute one source via coordinator and return source-scoped summary."""
    summary = context.resources.run_coordinator.run(
        trigger_type="on_demand",
        requested_by="dagit_asset_materialization",
        source_keys=[source_key],
    )
    cadence_def = SOURCE_CADENCE_DEFINITIONS.get(source_key)
    return {
        "run_id": summary["run_id"],
        "source_key": source_key,
        "outcome_state": summary["outcome_state"],
        "executed_source_count": summary["executed_source_count"],
        "failed_source_count": summary["failed_source_count"],
        "schedule_cadence": cadence_def[1] if cadence_def else "unknown",
        "schedule_owner": f"{source_key}_schedule",
    }


def _run_series_item(
    *,
    context,
    source_key: str,
    series_item_key: str,
) -> dict[str, Any]:
    """Execute one series item through a source workflow and return summary."""
    summary = context.resources.run_coordinator.run(
        trigger_type="on_demand",
        requested_by="dagit_series_materialization",
        source_keys=[source_key],
        series_item_keys=[series_item_key],
    )
    cadence_def = SOURCE_CADENCE_DEFINITIONS.get(source_key)
    return {
        "run_id": summary["run_id"],
        "source_key": source_key,
        "series_item_key": series_item_key,
        "outcome_state": summary["outcome_state"],
        "executed_source_count": summary["executed_source_count"],
        "failed_source_count": summary["failed_source_count"],
        "schedule_cadence": cadence_def[1] if cadence_def else "unknown",
        "schedule_owner": f"{source_key}_schedule",
    }


def _asset_name_for_series_item(*, provider_group_key: str, series_item_key: str) -> str:
    prefix = f"{provider_group_key}_"
    normalized = (
        series_item_key[len(prefix) :] if series_item_key.startswith(prefix) else series_item_key
    )
    return normalized.replace("-", "_")


def _make_series_source_asset(
    *,
    source_key: str,
    provider_group_key: str,
    series_item_key: str,
):
    @asset(
        name=_asset_name_for_series_item(
            provider_group_key=provider_group_key,
            series_item_key=series_item_key,
        ),
        key_prefix=provider_group_key,
        required_resource_keys={"run_coordinator"},
    )
    def _source_asset(context) -> dict[str, Any]:
        return _run_series_item(
            context=context,
            source_key=source_key,
            series_item_key=series_item_key,
        )

    return _source_asset


_DISCOVERED_SOURCE_SPECS = scan_adapter_modules()

_SOURCE_ASSET_REGISTRY: dict[str, Any] = {}
for spec in _DISCOVERED_SOURCE_SPECS:
    for series_item_key in spec.series_item_keys:
        _SOURCE_ASSET_REGISTRY[series_item_key] = _make_series_source_asset(
            source_key=spec.source_key,
            provider_group_key=spec.provider_group_key,
            series_item_key=series_item_key,
        )


SOURCE_DAGIT_ASSETS = [
    _SOURCE_ASSET_REGISTRY[series_item_key] for series_item_key in sorted(_SOURCE_ASSET_REGISTRY)
]
