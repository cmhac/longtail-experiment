"""Runtime wiring for orchestration ingest execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from src.contract.services.canonical_ingest_service import CanonicalIngestService

from .jobs.due_source_selector import DueSourceSelector
from .jobs.parallel_source_executor import ParallelSourceExecutor
from .jobs.run_coordinator import RunCoordinator
from .jobs.source_ingest_runner import SourceIngestRunner
from .jobs.source_schedule_policy import SourceSchedulePolicy
from .jobs.sources.dummy_source import build_dummy_source_workflow
from .jobs.sources.example_source import build_example_source_workflow
from .jobs.sources.fred_fedfunds_source import (
    FRED_FEDFUNDS_SOURCE_KEY,
    build_fred_fedfunds_source_workflow,
)
from .jobs.workflow_registry import SourceWorkflowRegistry
from .resources.postgres_observation_repository import PostgresObservationRepository
from .resources.postgres_run_repository import PostgresRunRepository
from .resources.source_lock_service import SourceLockService

EXPECTED_RUNTIME_SOURCE_KEYS = (
    "dummy_source",
    "example_source",
    FRED_FEDFUNDS_SOURCE_KEY,
)


class RuntimeWorkspaceLoadState(TypedDict):
    """Serialized runtime state used by local Dagit verification workflows."""

    workspace_loaded: bool
    errors: list[str]
    source_keys: tuple[str, ...]


@dataclass(frozen=True)
class IngestRuntime:
    """Container for orchestration runtime dependencies and stateful adapters."""

    run_coordinator: RunCoordinator
    source_lock_service: SourceLockService
    run_repository: PostgresRunRepository
    due_source_selector: DueSourceSelector
    parallel_source_executor: ParallelSourceExecutor

    def dagit_resources(self) -> dict[str, object]:
        """Return resource bindings exposed by Dagster definitions for local UI use."""
        return {
            "source_lock_service": self.source_lock_service,
            "run_coordinator": self.run_coordinator,
            "run_repository": self.run_repository,
            "due_source_selector": self.due_source_selector,
            "parallel_source_executor": self.parallel_source_executor,
        }


def verify_runtime_wiring_for_dagit(runtime: IngestRuntime) -> tuple[bool, list[str]]:
    """Validate that runtime wiring exposes resources and expected source registrations."""
    errors: list[str] = []

    resources = runtime.dagit_resources()
    for key in (
        "source_lock_service",
        "run_coordinator",
        "run_repository",
        "due_source_selector",
        "parallel_source_executor",
    ):
        if key not in resources:
            errors.append(f"Missing Dagit resource: {key}")

    registry = runtime.run_coordinator._workflow_registry  # noqa: SLF001 - runtime validation helper
    registered = tuple(registry.list_source_keys())
    for key in EXPECTED_RUNTIME_SOURCE_KEYS:
        if key not in registered:
            errors.append(f"Missing source workflow registration: {key}")

    return (len(errors) == 0, errors)


def get_runtime_workspace_load_state(runtime: IngestRuntime) -> RuntimeWorkspaceLoadState:
    """Expose a compact runtime load-state summary for local Dagit verification."""
    is_valid, errors = verify_runtime_wiring_for_dagit(runtime)
    registry = runtime.run_coordinator._workflow_registry  # noqa: SLF001 - verification helper

    return {
        "workspace_loaded": is_valid,
        "errors": errors,
        "source_keys": tuple(registry.list_source_keys()),
    }


def build_ingest_runtime() -> IngestRuntime:
    """Build the default ingest runtime used by Dagster definitions."""
    run_repository = PostgresRunRepository()
    observation_repository = PostgresObservationRepository()
    canonical_service = CanonicalIngestService(repository=observation_repository)
    runner = SourceIngestRunner(canonical_ingest_service=canonical_service)

    registry = SourceWorkflowRegistry()
    registry.register(
        build_dummy_source_workflow(
            runner,
            schedule_policy=SourceSchedulePolicy(
                source_key="dummy_source",
                cadence_type="hourly",
            ),
        )
    )
    registry.register(
        build_example_source_workflow(
            runner,
            schedule_policy=SourceSchedulePolicy(
                source_key="example_source",
                cadence_type="daily",
            ),
        )
    )
    registry.register(
        build_fred_fedfunds_source_workflow(
            runner,
            observation_repository=observation_repository,
            schedule_policy=SourceSchedulePolicy(
                source_key=FRED_FEDFUNDS_SOURCE_KEY,
                cadence_type="daily",
            ),
        )
    )

    source_lock_service = SourceLockService()
    due_source_selector = DueSourceSelector()
    parallel_source_executor = ParallelSourceExecutor(max_active_sources=2)
    run_coordinator = RunCoordinator(
        workflow_registry=registry,
        source_lock_service=source_lock_service,
        due_source_selector=due_source_selector,
        parallel_source_executor=parallel_source_executor,
        run_repository=run_repository,
    )

    return IngestRuntime(
        run_coordinator=run_coordinator,
        source_lock_service=source_lock_service,
        run_repository=run_repository,
        due_source_selector=due_source_selector,
        parallel_source_executor=parallel_source_executor,
    )
