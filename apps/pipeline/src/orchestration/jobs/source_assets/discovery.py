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
from ..sources.dummy_source import DUMMY_SOURCE_KEY, build_dummy_source_workflow
from ..sources.example_source import EXAMPLE_SOURCE_KEY, build_example_source_workflow
from ..sources.fred_fedfunds_source import (
    FRED_FEDFUNDS_SOURCE_KEY,
    ObservationCheckpointRepository,
    build_fred_fedfunds_source_workflow,
)
from ..sources.implementation_window_source import (
    IMPLEMENTATION_WINDOW_SOURCE_KEY,
    build_implementation_window_source_workflow,
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


def _build_default_specs() -> tuple[SourceBuilderSpec, ...]:
    return (
        SourceBuilderSpec(
            source_key=DUMMY_SOURCE_KEY,
            module_name="src.orchestration.jobs.sources.dummy_source",
            builder=lambda runner, observation_repository: build_dummy_source_workflow(
                runner,
                schedule_policy=SourceSchedulePolicy(
                    source_key=DUMMY_SOURCE_KEY,
                    cadence_type="hourly",
                ),
            ),
            provider_group_key="dummy",
            series_item_keys=("dummy_source",),
            canonical_series_keys=("DUMMY.SERIES",),
        ),
        SourceBuilderSpec(
            source_key=EXAMPLE_SOURCE_KEY,
            module_name="src.orchestration.jobs.sources.example_source",
            builder=lambda runner, observation_repository: build_example_source_workflow(
                runner,
                schedule_policy=SourceSchedulePolicy(
                    source_key=EXAMPLE_SOURCE_KEY,
                    cadence_type="daily",
                ),
            ),
            provider_group_key="example",
            series_item_keys=("example_source",),
            canonical_series_keys=("EXAMPLE.SERIES",),
        ),
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
        SourceBuilderSpec(
            source_key=IMPLEMENTATION_WINDOW_SOURCE_KEY,
            module_name="src.orchestration.jobs.sources.implementation_window_source",
            builder=lambda runner, observation_repository: (
                build_implementation_window_source_workflow(
                    runner,
                    schedule_policy=SourceSchedulePolicy(
                        source_key=IMPLEMENTATION_WINDOW_SOURCE_KEY,
                        cadence_type="daily",
                    ),
                )
            ),
            provider_group_key="implementation_window",
            series_item_keys=("implementation_window_source",),
            canonical_series_keys=("IMPLEMENTATION.WINDOW.SERIES",),
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
    by_source_key = sorted(discovered_specs, key=lambda spec: spec.source_key)

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
    by_source_key = sorted(discovered_specs, key=lambda spec: spec.source_key)
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
