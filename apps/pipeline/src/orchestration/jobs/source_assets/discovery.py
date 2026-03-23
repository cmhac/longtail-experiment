"""
Source discovery utilities for source-asset runtime registration.

NOTE (Feature 011): Source cadence metadata in SourceSchedulePolicy attached to
registrations is now used for operator visibility only. Active scheduling authority
is owned by per-source Dagster schedule definitions in source_asset_schedules.py.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..source_ingest_runner import SourceIngestRunner
from ..source_schedule_policy import SourceSchedulePolicy
from ..sources.fred_fedfunds_source import (
    FRED_FEDFUNDS_SOURCE_KEY,
    ObservationCheckpointRepository,
    build_fred_fedfunds_source_workflow,
)
from ..workflow_registry import SourceWorkflowRegistration
from .series_catalog import SeriesCatalogEntry


@dataclass(frozen=True)
class SourceBuilderSpec:
    """One discoverable source workflow builder declaration."""

    source_key: str
    module_name: str
    builder: Callable[
        [SourceIngestRunner, ObservationCheckpointRepository],
        SourceWorkflowRegistration,
    ]
    provider_group_key: str = ""
    series_item_keys: tuple[str, ...] = ()
    canonical_series_keys: tuple[str, ...] = ()
    ownership_mode: str = "grouped"


def is_adapter_spec(spec: SourceBuilderSpec) -> bool:
    """Return True when a spec is eligible for adapter registration discovery."""
    module_name = spec.module_name.strip()
    source_key = spec.source_key.strip()
    if not module_name or not source_key:
        return False
    # Adapter modules follow the *_source naming contract in this repository.
    return module_name.rsplit(".", 1)[-1].endswith("_source")


def filter_adapter_specs(
    specs: tuple[SourceBuilderSpec, ...],
) -> tuple[list[SourceBuilderSpec], list[SourceBuilderSpec]]:
    """Split specs into eligible adapter specs and ignored non-adapter specs."""
    eligible: list[SourceBuilderSpec] = []
    ignored: list[SourceBuilderSpec] = []
    for spec in specs:
        if is_adapter_spec(spec):
            eligible.append(spec)
        else:
            ignored.append(spec)
    return eligible, ignored


def _build_default_specs() -> tuple[SourceBuilderSpec, ...]:
    return (
        SourceBuilderSpec(
            source_key=FRED_FEDFUNDS_SOURCE_KEY,
            module_name="src.orchestration.jobs.sources.fred_fedfunds_source",
            builder=lambda runner, observation_repository: build_fred_fedfunds_source_workflow(
                runner,
                observation_repository=observation_repository,
                schedule_policy=SourceSchedulePolicy(
                    source_key=FRED_FEDFUNDS_SOURCE_KEY,
                    cadence_type="daily",
                ),
            ),
            provider_group_key="fred",
            series_item_keys=("fred_fedfunds", "fred_gasregw"),
            canonical_series_keys=("INT.US.FEDFUNDS", "ENERGY.US.GASREGW"),
        ),
    )


def discover_source_registrations(
    *,
    runner: SourceIngestRunner,
    observation_repository: ObservationCheckpointRepository,
    specs: tuple[SourceBuilderSpec, ...] | None = None,
) -> list[tuple[str, SourceWorkflowRegistration]]:
    """Discover and build source registrations in deterministic source-key order."""
    discovered_specs = specs or _build_default_specs()
    eligible_specs, _ignored_specs = filter_adapter_specs(discovered_specs)
    by_source_key = sorted(eligible_specs, key=lambda spec: spec.source_key)

    registrations: list[tuple[str, SourceWorkflowRegistration]] = []
    for spec in by_source_key:
        registration = spec.builder(runner, observation_repository)
        registrations.append((spec.module_name, registration))

    return registrations


def discover_series_catalog_entries(
    *,
    specs: tuple[SourceBuilderSpec, ...] | None = None,
) -> list[SeriesCatalogEntry]:
    """Discover runtime series catalog entries from source builder specs."""
    discovered_specs = specs or _build_default_specs()
    eligible_specs, _ignored_specs = filter_adapter_specs(discovered_specs)
    by_source_key = sorted(eligible_specs, key=lambda spec: spec.source_key)
    entries: list[SeriesCatalogEntry] = []
    for spec in by_source_key:
        if spec.series_item_keys and spec.canonical_series_keys:
            pairs = zip(spec.series_item_keys, spec.canonical_series_keys, strict=True)
            for series_item_key, canonical_series_key in pairs:
                entries.append(
                    SeriesCatalogEntry(
                        source_key=spec.source_key,
                        provider_group_key=(spec.provider_group_key or spec.source_key),
                        series_item_key=series_item_key,
                        canonical_series_key=canonical_series_key,
                        ownership_mode=spec.ownership_mode,
                    )
                )
            continue

        entries.append(
            SeriesCatalogEntry(
                source_key=spec.source_key,
                provider_group_key=(spec.provider_group_key or spec.source_key),
                series_item_key=spec.source_key,
                canonical_series_key=spec.source_key,
                ownership_mode=spec.ownership_mode,
            )
        )
    return entries
