"""Dagster definitions for ingestion orchestration."""

from dagster import Definitions

from .jobs.ingest_job import ingest_job
from .jobs.source_assets.recovery import build_post_cutover_recovery_plan
from .runtime import IngestRuntime, build_ingest_runtime
from .runtime import metadata_storage_enforcement_enabled, validate_dagster_metadata_storage_config
from .schedules.source_asset_schedules import SOURCE_ASSET_SCHEDULES
from .sensors.ondemand_sensor import ondemand_sensor
from .source_asset_definitions import SOURCE_DAGIT_ASSETS

if metadata_storage_enforcement_enabled():
    validate_dagster_metadata_storage_config()

_INGEST_RUNTIME = build_ingest_runtime()
DAGIT_WORKSPACE_MODULE = "src.orchestration.definitions"
WORKSPACE_DEFINITION_CATALOG: dict[str, tuple[str, ...]] = {
    "jobs": ("ingest_job",),
    "assets": tuple(sorted(asset.key.to_user_string() for asset in SOURCE_DAGIT_ASSETS)),
    "schedules": tuple(sorted(schedule_def.name for schedule_def in SOURCE_ASSET_SCHEDULES)),
    "sensors": ("ondemand_sensor",),
}


def get_ingest_runtime() -> IngestRuntime:
    """Return the default ingest runtime instance used by Dagster definitions."""
    return _INGEST_RUNTIME


def get_dagit_workspace_module() -> str:
    """Return the module path used by local Dagit startup helpers."""
    return DAGIT_WORKSPACE_MODULE


def get_workspace_definition_catalog() -> dict[str, tuple[str, ...]]:
    """Return the expected definitions exposed in the local Dagit workspace."""
    return WORKSPACE_DEFINITION_CATALOG


def get_scheduling_authority_mode() -> str:
    """Expose current scheduling authority mode for runtime verification checks."""
    return _INGEST_RUNTIME.authority_state.authority_mode


def get_recovery_plan_for_source_results(
    source_results: list[dict[str, object]],
) -> dict[str, object]:
    """Build post-cutover recovery plan from source-level outcomes."""
    return build_post_cutover_recovery_plan(
        authority_state=_INGEST_RUNTIME.authority_state,
        source_results=source_results,
    )


defs = Definitions(
    assets=SOURCE_DAGIT_ASSETS,
    jobs=[ingest_job],
    schedules=SOURCE_ASSET_SCHEDULES,
    sensors=[ondemand_sensor],
    resources=_INGEST_RUNTIME.dagit_resources(),
)
