"""Dagster job definition for orchestration ingest entrypoint."""

from __future__ import annotations

from typing import Any

from dagster import job, op

from .source_assets.recovery import build_post_cutover_recovery_plan
from .source_assets.series_selection import (
    normalize_requested_series_item_keys,
    resolve_series_selection,
)
from .source_assets.triggering import (
    build_invalid_source_request_summary,
    normalize_requested_source_keys,
    validate_source_selection,
)


@op(
    required_resource_keys={
        "run_coordinator",
        "scheduling_authority_state",
        "series_catalog_entries",
    }
)
def execute_ingest_run(context) -> dict[str, Any]:
    """Execute one coordinator-managed ingest run for all registered sources."""
    trigger_type_tag = context.run.tags.get("trigger_type", "scheduled")
    trigger_type = "on_demand" if trigger_type_tag == "on_demand" else "scheduled"
    requested_by = context.run.tags.get("requested_by", "dagster")
    requested_source_keys = normalize_requested_source_keys(
        source_key_tag=context.run.tags.get("source_key"),
        source_keys_tag=context.run.tags.get("source_keys"),
    )
    requested_series_item_keys = normalize_requested_series_item_keys(
        series_item_key_tag=context.run.tags.get("series_item_key"),
        series_item_keys_tag=context.run.tags.get("series_item_keys"),
    )

    run_coordinator = context.resources.run_coordinator
    available_source_keys = run_coordinator.list_registered_source_keys()
    selected_source_keys, invalid_source_keys = validate_source_selection(
        requested_source_keys=requested_source_keys,
        available_source_keys=available_source_keys,
    )

    series_selection = resolve_series_selection(
        requested_series_item_keys=requested_series_item_keys,
        catalog_entries=context.resources.series_catalog_entries,
        selected_source_keys=selected_source_keys,
    )

    if invalid_source_keys or series_selection.invalid_series_item_keys:
        invalid_keys = invalid_source_keys + series_selection.invalid_series_item_keys
        invalid_summary = build_invalid_source_request_summary(
            requested_by=requested_by,
            trigger_type=trigger_type,
            invalid_source_keys=invalid_keys,
            available_source_keys=available_source_keys,
        )
        context.log.error(
            "ingest run rejected due to invalid source or series selection",
            extra={
                "invalid_source_keys": invalid_source_keys,
                "invalid_series_item_keys": series_selection.invalid_series_item_keys,
                "available_source_keys": available_source_keys,
            },
        )
        return invalid_summary

    run_summary = run_coordinator.run(
        trigger_type=trigger_type,
        requested_by=requested_by,
        source_keys=series_selection.selected_source_keys,
        series_item_keys=series_selection.selected_series_item_keys,
    )
    context.log.info(
        "ingest run completed",
        extra={
            "run_id": run_summary["run_id"],
            "outcome_state": run_summary["outcome_state"],
            "accepted_count": run_summary["accepted_count"],
            "trigger_type": trigger_type,
            "trigger_origin": requested_by,
            "due_source_count": run_summary["due_source_count"],
            "executed_source_count": run_summary["executed_source_count"],
            "deferred_source_count": run_summary["deferred_source_count"],
            "not_due_source_count": run_summary["not_due_source_count"],
            "requested_source_keys": series_selection.selected_source_keys,
            "requested_series_item_keys": series_selection.selected_series_item_keys,
            "schedule_model": "per_source",
        },
    )
    if run_summary["deferred_source_count"] > 0:
        context.log.warning(
            "ingest run carried forward deferred due sources",
            extra={
                "run_id": run_summary["run_id"],
                "deferred_source_count": run_summary["deferred_source_count"],
            },
        )

    run_output: dict[str, Any] = dict(run_summary)

    if run_summary["failed_source_count"] > 0:
        authority_state = context.resources.scheduling_authority_state
        run_output["recovery_plan"] = build_post_cutover_recovery_plan(
            authority_state=authority_state,
            source_results=run_summary["source_results"],
        )

    return run_output


@job
def ingest_job() -> None:
    """Top-level Dagster job used by schedule and sensor triggers."""
    execute_ingest_run()
