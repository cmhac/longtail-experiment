"""Dagster job definition for orchestration ingest entrypoint."""

from __future__ import annotations

from typing import Any

from dagster import job, op


@op(required_resource_keys={"run_coordinator"})
def execute_ingest_run(context) -> dict[str, Any]:
    """Execute one coordinator-managed ingest run for all registered sources."""
    trigger_type_tag = context.run.tags.get("trigger_type", "scheduled")
    trigger_type = "on_demand" if trigger_type_tag == "on_demand" else "scheduled"
    requested_by = context.run.tags.get("requested_by", "dagster")

    run_summary = context.resources.run_coordinator.run(
        trigger_type=trigger_type,
        requested_by=requested_by,
    )
    context.log.info(
        "ingest run completed",
        extra={
            "run_id": run_summary["run_id"],
            "outcome_state": run_summary["outcome_state"],
            "accepted_count": run_summary["accepted_count"],
        },
    )
    return run_summary


@job
def ingest_job() -> None:
    """Top-level Dagster job used by schedule and sensor triggers."""
    execute_ingest_run()
