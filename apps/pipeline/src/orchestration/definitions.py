"""Dagster definitions for ingestion orchestration."""

from dagster import Definitions

from .jobs.ingest_job import ingest_job
from .resources.source_lock_service import SourceLockService
from .schedules.ingest_schedule import ingest_schedule
from .sensors.ondemand_sensor import ondemand_sensor

# Job wiring is intentionally lightweight while feature modules are maturing.
defs = Definitions(
    jobs=[ingest_job],
    schedules=[ingest_schedule],
    sensors=[ondemand_sensor],
    resources={"source_lock_service": SourceLockService()},
)
