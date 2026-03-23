"""Smoke test for Dagster orchestration definitions."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from dagster import Definitions

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.definitions import (
    defs,
    get_recovery_plan_for_source_results,
    get_scheduling_authority_mode,
    get_workspace_definition_catalog,
)
from src.orchestration.jobs.sources.fred_fedfunds_source import FRED_FEDFUNDS_SOURCE_KEY
from src.orchestration.jobs.sources.implementation_window_source import (
    IMPLEMENTATION_WINDOW_SOURCE_KEY,
)
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

    assert "test/dummy_source" in asset_keys
    assert "test/example_source" in asset_keys
    assert "fred/fedfunds" in asset_keys
    assert "fred/gasregw" in asset_keys


def test_runtime_builder_registers_expected_sources() -> None:
    """Runtime wiring should register baseline and implementation-window sources."""
    runtime = build_ingest_runtime()
    registry = runtime.run_coordinator._workflow_registry  # noqa: SLF001 - smoke assertion

    assert registry.list_source_keys() == [
        "dummy_source",
        "example_source",
        FRED_FEDFUNDS_SOURCE_KEY,
        IMPLEMENTATION_WINDOW_SOURCE_KEY,
    ]


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
    catalog = get_workspace_definition_catalog()

    assert catalog["jobs"] == ("ingest_job",)
    assert catalog["assets"] == (
        "test/dummy_source",
        "test/example_source",
        "fred/fedfunds",
        "fred/gasregw",
    )
    assert catalog["schedules"] == (
        "dummy_source_schedule",
        "example_source_schedule",
        "fred_fedfunds_schedule",
    )
    assert catalog["sensors"] == ("ondemand_sensor",)


def test_runtime_workspace_load_state_reports_loaded_for_default_runtime() -> None:
    """Runtime load-state summary should report successful workspace wiring."""
    runtime = build_ingest_runtime()
    load_state = get_runtime_workspace_load_state(runtime)

    assert load_state["workspace_loaded"] is True
    assert FRED_FEDFUNDS_SOURCE_KEY in load_state["source_keys"]
    assert IMPLEMENTATION_WINDOW_SOURCE_KEY in load_state["source_keys"]


def test_definitions_expose_dagster_only_authority_mode() -> None:
    """Definitions should expose dagster-only scheduling authority mode."""
    assert get_scheduling_authority_mode() == "dagster_only"


def test_definitions_recovery_plan_keeps_legacy_paths_disabled() -> None:
    """Recovery plans built from definitions should never re-enable legacy paths."""
    plan = get_recovery_plan_for_source_results(
        [
            {"source_key": "dummy_source", "status": "success"},
            {"source_key": "fred_fedfunds", "status": "failure"},
        ]
    )

    assert plan["authority_mode"] == "dagster_only"
    assert plan["legacy_paths_disabled"] is True
    assert plan["failed_sources"] == ["fred_fedfunds"]


def test_dagit_endpoint_probe_reports_ready_when_endpoint_is_reachable() -> None:
    """Endpoint probe helper should pass when target endpoint is reachable."""

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, format: str, *args: object) -> None:  # noqa: A002
            return

    server = HTTPServer(("127.0.0.1", 0), _Handler)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    repo_root = Path(__file__).resolve().parents[4]
    try:
        completed = subprocess.run(
            ["bash", "tools/quality/local-stack/test-dagit-endpoint.sh"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            env={
                **os.environ,
                "DAGIT_ENDPOINT": f"http://127.0.0.1:{port}",
                "DAGIT_VERIFY_WORKSPACE": "0",
            },
        )
    finally:
        server.shutdown()
        server.server_close()

    assert completed.returncode == 0
    assert "DAGIT_HEALTH_STATUS=ready" in completed.stdout


def test_dagit_endpoint_probe_reports_unavailable_for_unreachable_endpoint() -> None:
    """Endpoint probe should emit endpoint_unavailable when target is not reachable."""
    repo_root = Path(__file__).resolve().parents[4]
    completed = subprocess.run(
        ["bash", "tools/quality/local-stack/test-dagit-endpoint.sh"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "DAGIT_ENDPOINT": "http://127.0.0.1:9",
            "DAGIT_ENDPOINT_RETRIES": "1",
            "DAGIT_ENDPOINT_DELAY_SECONDS": "0",
        },
    )

    assert completed.returncode == 1
    assert "DAGIT_FAILURE_CATEGORY=endpoint_unavailable" in completed.stdout


def test_no_shared_all_source_schedule_in_definitions() -> None:
    """Feature 011 regression: shared ingest_schedule must not exist in definitions."""
    schedule_names = {schedule_def.name for schedule_def in (defs.schedules or [])}
    assert "ingest_schedule" not in schedule_names


def test_per_source_schedules_registered_in_definitions() -> None:
    """Feature 011: each active source should have its own schedule in definitions."""
    schedule_names = {schedule_def.name for schedule_def in (defs.schedules or [])}
    assert "dummy_source_schedule" in schedule_names
    assert "example_source_schedule" in schedule_names
    assert "fred_fedfunds_schedule" in schedule_names


def test_grouped_fred_series_share_default_cadence_definition() -> None:
    """Grouped series items should inherit one shared cadence by default."""
    assert SOURCE_CADENCE_DEFINITIONS["fred_fedfunds"][1] == "daily"
    assert SOURCE_SERIES_ITEM_DEFINITIONS["fred_fedfunds"] == (
        "fred_fedfunds",
        "fred_gasregw",
    )
