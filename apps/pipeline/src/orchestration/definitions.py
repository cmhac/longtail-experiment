"""Dagster definitions for ingestion orchestration."""

from dagster import Definitions

from .jobs.ingest_job import ingest_job
from .runtime import IngestRuntime, build_ingest_runtime
from .schedules.ingest_schedule import ingest_schedule
from .sensors.ondemand_sensor import ondemand_sensor

_INGEST_RUNTIME = build_ingest_runtime()


def get_ingest_runtime() -> IngestRuntime:
    """Return the default ingest runtime instance used by Dagster definitions."""
    return _INGEST_RUNTIME


defs = Definitions(
    jobs=[ingest_job],
    schedules=[ingest_schedule],
    sensors=[ondemand_sensor],
    resources={
        "source_lock_service": _INGEST_RUNTIME.source_lock_service,
        "run_coordinator": _INGEST_RUNTIME.run_coordinator,
        "run_repository": _INGEST_RUNTIME.run_repository,
    },
)
