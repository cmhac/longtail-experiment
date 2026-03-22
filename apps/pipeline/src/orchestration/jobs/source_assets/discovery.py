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


@dataclass(frozen=True)
class SourceBuilderSpec:
    """One discoverable source workflow builder declaration."""

    source_key: str
    module_name: str
    builder: Callable[
        [SourceIngestRunner, ObservationCheckpointRepository],
        SourceWorkflowRegistration,
    ]


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
