"""Dagster asset definitions for source-level visibility in Dagit."""

from __future__ import annotations

from typing import Any

from dagster import asset


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
    return {
        "run_id": summary["run_id"],
        "source_key": source_key,
        "outcome_state": summary["outcome_state"],
        "executed_source_count": summary["executed_source_count"],
        "failed_source_count": summary["failed_source_count"],
    }


@asset(name="dummy_source", required_resource_keys={"run_coordinator"})
def dummy_source_asset(context) -> dict[str, Any]:
    """Materialize source visibility entry for dummy_source."""
    return _run_single_source(context=context, source_key="dummy_source")


@asset(name="example_source", required_resource_keys={"run_coordinator"})
def example_source_asset(context) -> dict[str, Any]:
    """Materialize source visibility entry for example_source."""
    return _run_single_source(context=context, source_key="example_source")


@asset(name="fred_fedfunds", required_resource_keys={"run_coordinator"})
def fred_fedfunds_source_asset(context) -> dict[str, Any]:
    """Materialize source visibility entry for fred_fedfunds."""
    return _run_single_source(context=context, source_key="fred_fedfunds")


SOURCE_DAGIT_ASSETS = [
    dummy_source_asset,
    example_source_asset,
    fred_fedfunds_source_asset,
]
