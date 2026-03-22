"""On-demand Dagster sensor for operator-triggered ingestion runs."""

from __future__ import annotations

from dagster import RunRequest, SkipReason, sensor


@sensor(job_name="ingest_job")
def ondemand_sensor(context):
    """Emit on-demand run requests when a cursor token is present."""
    token = context.cursor
    if token is None or not token.strip():
        return SkipReason("no queued on-demand trigger")
    context.update_cursor("")
    return RunRequest(
        run_key=token,
        tags={
            "trigger_type": "on_demand",
            "requested_by": "ondemand_sensor",
            "source_selection_mode": "operator_requested",
        },
    )
