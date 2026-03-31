"""Runtime wiring for orchestration ingest execution."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import TypedDict, cast

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
from .jobs.source_assets.discovery import (
    discover_series_catalog_entries,
    discover_source_registrations,
    scan_adapter_modules,
)
from .jobs.source_assets.ownership_mode import (
    SeriesOwnershipModeRecord,
    build_ownership_mode_registry,
)
from .jobs.source_assets.series_catalog import (
    SeriesCatalogEntry,
    validate_series_catalog_entries,
)
from .jobs.source_ingest_runner import SourceIngestRunner
from .jobs.workflow_registry import SourceWorkflowRegistry
from .resources.postgres_observation_repository import PostgresObservationRepository
from .resources.postgres_run_repository import PostgresRunRepository
from .resources.source_lock_service import SourceLockService

logger = logging.getLogger(__name__)

EXPECTED_RUNTIME_SOURCE_KEYS = tuple(spec.source_key for spec in scan_adapter_modules())

RETIRED_LEGACY_CADENCE_ENTRYPOINTS = (
    "legacy_scheduler",
    "legacy_coordinator",
)

ACTIVE_SCHEDULE_MODEL = "per_source"
"""Post-cutover schedule model: each source asset owns its own Dagster schedule."""

REQUIRED_DAGSTER_METADATA_ENV_VARS: tuple[str, ...] = (
    "DAGSTER_METADATA_DB_HOST",
    "DAGSTER_METADATA_DB_PORT",
    "DAGSTER_METADATA_DB_NAME",
    "DAGSTER_METADATA_DB_USER",
    "DAGSTER_METADATA_DB_PASSWORD",
)

FORBIDDEN_TREND_OVERRIDE_ENV_VARS: tuple[str, ...] = (
    "LONGTAIL_TREND_THRESHOLD",
    "LONGTAIL_TREND_CADENCE_WINDOW",
    "LONGTAIL_TREND_SEASONALITY_WINDOW",
)


def metadata_storage_enforcement_enabled() -> bool:
    """Return whether metadata DB env validation is enforced for Dagster startup."""
    return os.getenv("DAGSTER_METADATA_ENFORCE", "0").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def get_dagster_metadata_storage_config() -> dict[str, str]:
    """Return resolved metadata DB env values for Dagster storage configuration."""
    return {key: os.getenv(key, "").strip() for key in REQUIRED_DAGSTER_METADATA_ENV_VARS}


def validate_dagster_metadata_storage_config() -> dict[str, str]:
    """Validate required metadata DB env values and raise on missing entries."""
    config = get_dagster_metadata_storage_config()
    missing = sorted(key for key, value in config.items() if not value)
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            "Missing required Dagster metadata DB environment variables: "
            f"{joined}. Dagster metadata storage is configured for PostgreSQL; "
            "do not fall back to SQLite."
        )
    return config


def validate_trend_runtime_defaults_policy() -> None:
    """Fail fast if runtime attempts to override hardcoded trend defaults."""
    configured = sorted(
        key for key in FORBIDDEN_TREND_OVERRIDE_ENV_VARS if os.getenv(key, "").strip() != ""
    )
    if configured:
        joined = ", ".join(configured)
        raise RuntimeError(
            "Trend analysis defaults are library-owned and cannot be overridden via "
            f"environment variables: {joined}"
        )


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
    series_outcomes: list[dict[str, object]]


@dataclass(frozen=True)
class IngestRuntime:
    """Container for orchestration runtime dependencies and stateful adapters."""

    run_coordinator: RunCoordinator
    source_lock_service: SourceLockService
    run_repository: PostgresRunRepository
    due_source_selector: DueSourceSelector
    parallel_source_executor: ParallelSourceExecutor
    authority_state: SchedulingAuthorityState
    series_catalog_entries: tuple[SeriesCatalogEntry, ...]
    ownership_mode_registry: dict[str, SeriesOwnershipModeRecord]

    def dagit_resources(self) -> dict[str, object]:
        """Return resource bindings exposed by Dagster definitions for local UI use."""
        return {
            "source_lock_service": self.source_lock_service,
            "run_coordinator": self.run_coordinator,
            "run_repository": self.run_repository,
            "due_source_selector": self.due_source_selector,
            "parallel_source_executor": self.parallel_source_executor,
            "scheduling_authority_state": self.authority_state,
            "series_catalog_entries": self.series_catalog_entries,
            "ownership_mode_registry": self.ownership_mode_registry,
        }


def map_source_outcomes_to_persistence_records(
    source_results: list[dict[str, object]],
    *,
    trigger_origin: str | None = None,
) -> list[SourceOutcomePersistenceRecord]:
    """Normalize run source outcomes into persistence-view records."""
    mapped: list[SourceOutcomePersistenceRecord] = []
    for source_result in source_results:
        raw_series_outcomes = source_result.get("series_outcomes")
        series_outcomes: list[dict[str, object]] = (
            cast(list[dict[str, object]], raw_series_outcomes)
            if isinstance(raw_series_outcomes, list)
            else []
        )
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
                "series_outcomes": list(series_outcomes),
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

    registered = runtime.run_coordinator.list_registered_source_keys()
    for key in EXPECTED_RUNTIME_SOURCE_KEYS:
        if key not in registered:
            errors.append(f"Missing source workflow registration: {key}")

    return (len(errors) == 0, errors)


def get_runtime_workspace_load_state(runtime: IngestRuntime) -> RuntimeWorkspaceLoadState:
    """Expose a compact runtime load-state summary for local Dagit verification."""
    is_valid, errors = verify_runtime_wiring_for_dagit(runtime)

    return {
        "workspace_loaded": is_valid,
        "errors": errors,
        "source_keys": tuple(runtime.run_coordinator.list_registered_source_keys()),
    }


def build_ingest_runtime() -> IngestRuntime:
    """Build the default ingest runtime used by Dagster definitions."""
    validate_trend_runtime_defaults_policy()
    run_repository = PostgresRunRepository()
    observation_repository = PostgresObservationRepository()
    canonical_service = CanonicalIngestService(repository=observation_repository)
    runner = SourceIngestRunner(canonical_ingest_service=canonical_service)

    registry = SourceWorkflowRegistry()
    series_catalog_entries = discover_series_catalog_entries()
    validate_series_catalog_entries(series_catalog_entries)

    ownership_mode_records = [
        SeriesOwnershipModeRecord(
            series_item_key=entry.series_item_key,
            owner_adapter_key=entry.source_key,
            mode="grouped" if entry.ownership_mode == "grouped" else "split",
        )
        for entry in series_catalog_entries
    ]
    ownership_mode_registry = build_ownership_mode_registry(ownership_mode_records)

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
                "discovered_provider_group_keys": sorted(
                    {entry.provider_group_key for entry in series_catalog_entries}
                ),
                "discovered_series_item_keys": sorted(
                    {entry.series_item_key for entry in series_catalog_entries}
                ),
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
        series_catalog_entries=tuple(series_catalog_entries),
        ownership_mode_registry=ownership_mode_registry,
    )

    return IngestRuntime(
        run_coordinator=run_coordinator,
        source_lock_service=source_lock_service,
        run_repository=run_repository,
        due_source_selector=due_source_selector,
        parallel_source_executor=parallel_source_executor,
        authority_state=authority_state,
        series_catalog_entries=tuple(series_catalog_entries),
        ownership_mode_registry=ownership_mode_registry,
    )
