"""Runtime wiring for orchestration ingest execution."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TypedDict

from src.contract.services.canonical_ingest_service import CanonicalIngestService

from .jobs.due_source_selector import DueSourceSelector
from .jobs.parallel_source_executor import ParallelSourceExecutor
from .jobs.run_coordinator import RunCoordinator
from .jobs.source_assets.authority_state import (
    SchedulingAuthorityState,
    assert_dagster_only_authority,
    dagster_only_authority_state,
)
from .jobs.source_assets.contracts import SourceAssetContractError, register_source_assets
from .jobs.source_assets.discovery import discover_source_registrations
from .jobs.source_ingest_runner import SourceIngestRunner
from .jobs.sources.fred_fedfunds_source import FRED_FEDFUNDS_SOURCE_KEY
from .jobs.sources.implementation_window_source import IMPLEMENTATION_WINDOW_SOURCE_KEY
from .jobs.workflow_registry import SourceWorkflowRegistry
from .resources.postgres_observation_repository import PostgresObservationRepository
from .resources.postgres_run_repository import PostgresRunRepository
from .resources.source_lock_service import SourceLockService

logger = logging.getLogger(__name__)

EXPECTED_RUNTIME_SOURCE_KEYS = (
    "dummy_source",
    "example_source",
    FRED_FEDFUNDS_SOURCE_KEY,
    IMPLEMENTATION_WINDOW_SOURCE_KEY,
)

RETIRED_LEGACY_CADENCE_ENTRYPOINTS = (
    "legacy_scheduler",
    "legacy_coordinator",
)

ACTIVE_SCHEDULE_MODEL = "per_source"
"""Post-cutover schedule model: each source asset owns its own Dagster schedule."""


class RuntimeWorkspaceLoadState(TypedDict):
    """Serialized runtime state used by local Dagit verification workflows."""

    workspace_loaded: bool
    errors: list[str]
    source_keys: tuple[str, ...]


class SourceOutcomePersistenceRecord(TypedDict):
    """Runtime-shaped source outcome record persisted for operator visibility."""

    source_key: str
    state: str
    outcome_reason_code: str | None
    message: str | None
    visible_in_dagit: bool
    failure_summary: str | None


@dataclass(frozen=True)
class IngestRuntime:
    """Container for orchestration runtime dependencies and stateful adapters."""

    run_coordinator: RunCoordinator
    source_lock_service: SourceLockService
    run_repository: PostgresRunRepository
    due_source_selector: DueSourceSelector
    parallel_source_executor: ParallelSourceExecutor
    authority_state: SchedulingAuthorityState

    def dagit_resources(self) -> dict[str, object]:
        """Return resource bindings exposed by Dagster definitions for local UI use."""
        return {
            "source_lock_service": self.source_lock_service,
            "run_coordinator": self.run_coordinator,
            "run_repository": self.run_repository,
            "due_source_selector": self.due_source_selector,
            "parallel_source_executor": self.parallel_source_executor,
            "scheduling_authority_state": self.authority_state,
        }


def map_source_outcomes_to_persistence_records(
    source_results: list[dict[str, object]],
    *,
    trigger_origin: str | None = None,
) -> list[SourceOutcomePersistenceRecord]:
    """Normalize run source outcomes into persistence-view records."""
    mapped: list[SourceOutcomePersistenceRecord] = []
    for source_result in source_results:
        mapped.append(
            {
                "source_key": str(source_result["source_key"]),
                "state": str(source_result["status"]),
                "outcome_reason_code": (
                    str(source_result["outcome_reason_code"])
                    if source_result.get("outcome_reason_code") is not None
                    else None
                ),
                "message": (
                    str(source_result["message"])
                    if source_result.get("message") is not None
                    else None
                ),
                "visible_in_dagit": bool(source_result.get("visible_in_dagit", True)),
                "failure_summary": (
                    str(source_result["failure_summary"])
                    if source_result.get("failure_summary") is not None
                    else None
                ),
            }
        )
    return mapped


def assert_legacy_cadence_entrypoints_retired(*, authority_state: SchedulingAuthorityState) -> None:
    """Ensure legacy cadence paths remain disabled after cutover."""
    assert_dagster_only_authority(authority_state)


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
        "scheduling_authority_state",
    ):
        if key not in resources:
            errors.append(f"Missing Dagit resource: {key}")

    authority_state = resources["scheduling_authority_state"]
    if isinstance(authority_state, SchedulingAuthorityState):
        try:
            assert_dagster_only_authority(authority_state)
            assert_legacy_cadence_entrypoints_retired(authority_state=authority_state)
        except RuntimeError as exc:
            errors.append(str(exc))

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
    try:
        discovered = discover_source_registrations(
            runner=runner,
            observation_repository=observation_repository,
        )
        logger.info(
            "source asset discovery completed",
            extra={
                "discovered_source_count": len(discovered),
                "discovered_source_keys": [
                    registration.source_key for _, registration in discovered
                ],
                "telemetry_event": "source_asset_discovery",
            },
        )
        register_source_assets(registry=registry, registrations=discovered)
    except SourceAssetContractError as exc:
        logger.error(
            "source asset contract validation failed",
            extra={
                "module_name": exc.module_name,
                "source_key": exc.source_key,
                "contract_reason": exc.reason,
                "telemetry_event": "source_asset_contract_failure",
            },
        )
        raise

    source_lock_service = SourceLockService()
    due_source_selector = DueSourceSelector()
    parallel_source_executor = ParallelSourceExecutor(max_active_sources=2)
    authority_state = dagster_only_authority_state(partial_failure_mode=False)
    assert_legacy_cadence_entrypoints_retired(authority_state=authority_state)
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
        authority_state=authority_state,
    )
