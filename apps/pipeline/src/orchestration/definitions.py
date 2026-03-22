"""Dagster definitions for ingestion orchestration."""

from dagster import Definitions

from .jobs.ingest_job import ingest_job
from .runtime import IngestRuntime, build_ingest_runtime
from .schedules.ingest_schedule import ingest_schedule
from .sensors.ondemand_sensor import ondemand_sensor

_INGEST_RUNTIME = build_ingest_runtime()
DAGIT_WORKSPACE_MODULE = "src.orchestration.definitions"
WORKSPACE_DEFINITION_CATALOG: dict[str, tuple[str, ...]] = {
    "jobs": ("ingest_job",),
    "schedules": ("ingest_schedule",),
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


defs = Definitions(
    jobs=[ingest_job],
    schedules=[ingest_schedule],
    sensors=[ondemand_sensor],
    resources=_INGEST_RUNTIME.dagit_resources(),
)
