"""Runtime wiring for orchestration ingest execution."""

from __future__ import annotations

from dataclasses import dataclass

from src.contract.services.canonical_ingest_service import CanonicalIngestService

from .jobs.due_source_selector import DueSourceSelector
from .jobs.parallel_source_executor import ParallelSourceExecutor
from .jobs.run_coordinator import RunCoordinator
from .jobs.source_ingest_runner import SourceIngestRunner
from .jobs.source_schedule_policy import SourceSchedulePolicy
from .jobs.sources.dummy_source import build_dummy_source_workflow
from .jobs.sources.example_source import build_example_source_workflow
from .jobs.workflow_registry import SourceWorkflowRegistry
from .resources.postgres_run_repository import PostgresRunRepository
from .resources.source_lock_service import SourceLockService


class _DiscardingObservationRepository:
    """No-op observation repository used until canonical DB tables are migrated."""

    def upsert_observation(self, _observation: object) -> None:
        """Accept validated observations without retaining in-memory runtime state."""


@dataclass(frozen=True)
class IngestRuntime:
    """Container for orchestration runtime dependencies and stateful adapters."""

    run_coordinator: RunCoordinator
    source_lock_service: SourceLockService
    run_repository: PostgresRunRepository
    due_source_selector: DueSourceSelector
    parallel_source_executor: ParallelSourceExecutor


def build_ingest_runtime() -> IngestRuntime:
    """Build the default ingest runtime used by Dagster definitions."""
    run_repository = PostgresRunRepository()
    canonical_service = CanonicalIngestService(repository=_DiscardingObservationRepository())
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
