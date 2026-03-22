"""Scheduled Dagster trigger for standardized ingestion runs."""

from __future__ import annotations

from dagster import RunRequest, schedule


@schedule(cron_schedule="0 * * * *", job_name="ingest_job")
def ingest_schedule(_context) -> RunRequest:
    """Emit hourly scheduled run requests for ingestion operations."""
    return RunRequest(run_key=None, tags={"trigger_type": "scheduled"})
