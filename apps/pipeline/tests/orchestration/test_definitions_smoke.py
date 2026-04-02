"""Smoke test for Dagster orchestration definitions."""

from __future__ import annotations

import sys
from pathlib import Path

from dagster import Definitions

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.definitions import (
    defs,
    get_recovery_plan_for_source_results,
    get_scheduling_authority_mode,
    get_trend_stage_dependencies,
    get_workspace_definition_catalog,
)
from src.orchestration.jobs.source_assets.discovery import scan_adapter_modules
from src.orchestration.runtime import (
    build_ingest_runtime,
    get_runtime_workspace_load_state,
    verify_runtime_wiring_for_dagit,
)
from src.orchestration.schedules.source_asset_schedules import (
    SOURCE_CADENCE_DEFINITIONS,
    SOURCE_SERIES_ITEM_DEFINITIONS,
)


def test_orchestration_definitions_is_dagster_definitions() -> None:
    """The orchestration entrypoint must expose a Dagster Definitions object."""
    assert isinstance(defs, Definitions)


def test_orchestration_definitions_expose_visibility_resources() -> None:
    """Definitions should include resources needed for visibility and scheduling semantics."""
    resources = defs.resources or {}
    assert "run_repository" in resources
    assert "due_source_selector" in resources
    assert "parallel_source_executor" in resources


def test_definitions_expose_source_assets_for_dagit_catalog() -> None:
    """Dagit definitions should surface source-per-asset entries in the catalog."""
    asset_keys = {asset_key.to_user_string() for asset_key in defs.resolve_all_asset_keys()}

    assert "fred/fedfunds" in asset_keys
    assert "fred/gasregw" in asset_keys


def test_runtime_builder_registers_expected_sources() -> None:
    """Runtime wiring should register active source adapters."""
    runtime = build_ingest_runtime()
    registry = runtime.run_coordinator._workflow_registry  # noqa: SLF001 - smoke assertion
    expected_source_keys = [spec.source_key for spec in scan_adapter_modules()]

    assert registry.list_source_keys() == expected_source_keys


def test_runtime_registry_order_is_deterministic() -> None:
    """Runtime registry list should remain deterministic for a fixed adapter set."""
    first_runtime = build_ingest_runtime()
    second_runtime = build_ingest_runtime()
    first_registry = first_runtime.run_coordinator._workflow_registry  # noqa: SLF001
    second_registry = second_runtime.run_coordinator._workflow_registry  # noqa: SLF001

    assert first_registry.list_source_keys() == second_registry.list_source_keys()


def test_definitions_expose_ingest_job_for_dagit_workspace() -> None:
    """Dagit workspace loading should surface ingest job definition by name."""
    assert defs.get_job_def("ingest_job").name == "ingest_job"


def test_runtime_wiring_validation_passes_for_dagit() -> None:
    """Runtime builder should satisfy Dagit resource and source registration checks."""
    runtime = build_ingest_runtime()
    is_valid, errors = verify_runtime_wiring_for_dagit(runtime)

    assert is_valid
    assert errors == []


def test_workspace_definition_catalog_lists_existing_definitions() -> None:
    """Workspace catalog should list expected definitions for local Dagit visibility."""
    expected_specs = scan_adapter_modules()

    def _asset_key(provider_group_key: str, series_item_key: str) -> str:
        asset_name = series_item_key.split(f"{provider_group_key}_", 1)[-1].replace("-", "_")
        return f"{provider_group_key}/{asset_name}"

    expected_assets: tuple[str, ...] = tuple(
        sorted(
            _asset_key(spec.provider_group_key, series_item_key)
            for spec in expected_specs
            for series_item_key in spec.series_item_keys
        )
    )
    expected_schedules = tuple(sorted(f"{spec.source_key}_schedule" for spec in expected_specs))

    catalog = get_workspace_definition_catalog()

    assert catalog["jobs"] == ("ingest_job",)
    assert catalog["assets"] == expected_assets
    assert catalog["schedules"] == expected_schedules
    assert catalog["sensors"] == ("ondemand_sensor",)


def test_runtime_workspace_load_state_reports_loaded_for_default_runtime() -> None:
    """Runtime load-state summary should report successful workspace wiring."""
    runtime = build_ingest_runtime()
    load_state = get_runtime_workspace_load_state(runtime)
    expected_source_keys = tuple(spec.source_key for spec in scan_adapter_modules())

    assert load_state["workspace_loaded"] is True
    assert load_state["source_keys"] == expected_source_keys


def test_definitions_expose_dagster_only_authority_mode() -> None:
    """Definitions should expose dagster-only scheduling authority mode."""
    assert get_scheduling_authority_mode() == "dagster_only"


def test_definitions_recovery_plan_keeps_legacy_paths_disabled() -> None:
    """Recovery plans built from definitions should never re-enable legacy paths."""
    first_source_key = scan_adapter_modules()[0].source_key
    plan = get_recovery_plan_for_source_results(
        [
            {"source_key": first_source_key, "status": "success"},
            {"source_key": first_source_key, "status": "failure"},
        ]
    )

    assert plan["authority_mode"] == "dagster_only"
    assert plan["legacy_paths_disabled"] is True
    assert plan["failed_sources"] == [first_source_key]


def test_definitions_expose_trend_stage_dependency_surface() -> None:
    """Trend stage metadata should expose its fetch/update dependency surface."""
    assert get_trend_stage_dependencies() == ("per_series_source_asset_outputs",)


def test_compose_dagit_healthcheck_queries_workspace_graphql() -> None:
    """Compose health should validate workspace GraphQL, not only the root page."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "http://localhost:3000/graphql" in compose
    assert "workspaceOrError" in compose
    assert "locationEntries" in compose


def test_no_shared_all_source_schedule_in_definitions() -> None:
    """Feature 011 regression: shared ingest_schedule must not exist in definitions."""
    schedule_names = {schedule_def.name for schedule_def in (defs.schedules or [])}
    assert "ingest_schedule" not in schedule_names


def test_per_source_schedules_registered_in_definitions() -> None:
    """Feature 011: each active source should have its own schedule in definitions."""
    expected_schedule_names = {f"{spec.source_key}_schedule" for spec in scan_adapter_modules()}
    schedule_names = {schedule_def.name for schedule_def in (defs.schedules or [])}
    assert expected_schedule_names.issubset(schedule_names)


def test_grouped_fred_series_share_default_cadence_definition() -> None:
    """Grouped series items should inherit one shared cadence by default per adapter."""
    for spec in scan_adapter_modules():
        assert SOURCE_CADENCE_DEFINITIONS[spec.source_key][1] == spec.cadence_label
        assert SOURCE_SERIES_ITEM_DEFINITIONS[spec.source_key] == spec.series_item_keys


def test_compose_declares_dual_database_health_dependencies_for_dagit() -> None:
    """Dagit should depend on both canonical and metadata database health checks."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "dagster_db:" in compose
    assert "depends_on:" in compose
    assert 'DAGSTER_METADATA_ENFORCE: "1"' in compose


def test_compose_dagit_healthcheck_requires_loaded_workspace_entries() -> None:
    """Dagit healthcheck should require at least one workspace location entry."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "len(entries) >= 1" in compose
