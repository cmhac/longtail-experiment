"""
Per-source asset Dagster schedule definitions.

Each active source asset owns its own schedule targeting ingest_job with
source-specific tags. This replaces the retired shared ingest_schedule.
"""

from __future__ import annotations

from dagster import RunRequest, schedule

from ..jobs.source_assets.discovery import scan_adapter_modules

_DISCOVERED_SOURCE_SPECS = scan_adapter_modules()

# --- Source cadence configuration ---
# Maps source_key -> (cron_schedule, human-readable cadence label)
SOURCE_CADENCE_DEFINITIONS: dict[str, tuple[str, str]] = {
    spec.source_key: (spec.cron_schedule, spec.cadence_label) for spec in _DISCOVERED_SOURCE_SPECS
}

SOURCE_SERIES_ITEM_DEFINITIONS: dict[str, tuple[str, ...]] = {
    spec.source_key: spec.series_item_keys for spec in _DISCOVERED_SOURCE_SPECS
}

SOURCE_PROVIDER_GROUP_DEFINITIONS: dict[str, str] = {
    spec.source_key: spec.provider_group_key for spec in _DISCOVERED_SOURCE_SPECS
}


def _make_source_schedule(source_key: str, cron: str, cadence_label: str):
    """Build a Dagster schedule for one source asset."""

    @schedule(
        cron_schedule=cron,
        job_name="ingest_job",
        name=f"{source_key}_schedule",
    )
    def source_schedule(_context) -> RunRequest:
        series_item_keys = SOURCE_SERIES_ITEM_DEFINITIONS.get(source_key, (source_key,))
        return RunRequest(
            run_key=None,
            tags={
                "trigger_type": "scheduled",
                "source_selection_mode": "source_owned",
                "requested_by": f"{source_key}_schedule",
                "source_keys": source_key,
                "cadence_label": cadence_label,
                "provider_group_key": SOURCE_PROVIDER_GROUP_DEFINITIONS.get(
                    source_key,
                    source_key,
                ),
                "series_item_keys": ",".join(series_item_keys),
            },
        )

    source_schedule.__doc__ = f"Emit scheduled run requests for {source_key} ({cadence_label})."
    return source_schedule


SOURCE_ASSET_SCHEDULES = [
    _make_source_schedule(source_key, cron_schedule, cadence_label)
    for source_key, (cron_schedule, cadence_label) in sorted(SOURCE_CADENCE_DEFINITIONS.items())
]
