"""Integration tests for Dagster ingest job runtime execution."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.definitions import defs, get_ingest_runtime
from src.orchestration.jobs.sources.fred_fedfunds_source import FRED_FEDFUNDS_SOURCE_KEY
from src.orchestration.jobs.workflow_result import map_dagit_failure_category
from src.orchestration.resources.postgres_observation_repository import (
    PostgresObservationRepository,
)


def test_ingest_job_executes_and_persists_fred_source_outcomes() -> None:
    """Dagster ingest job should persist run and FRED source outcome rows in Postgres."""
    if not os.getenv("FRED_API_KEY", "").strip():
        pytest.skip("FRED_API_KEY not set; skipping live FRED ingest job integration")

    runtime = get_ingest_runtime()
    run_repo = runtime.run_repository
    observation_repo = PostgresObservationRepository()

    probe_run_id = f"run-probe-{uuid4()}"
    try:
        run_repo.fetch_run(probe_run_id)
        observation_repo.read_latest_observed_on(series_key="INT.US.FEDFUNDS")
    except Exception as exc:  # pragma: no cover - environment-dependent integration guard
        pytest.skip(f"postgres runtime DB unavailable for integration test: {exc}")

    run_repo.clear_all()
    observation_repo.clear_all()

    result = defs.get_job_def("ingest_job").execute_in_process(
        run_config={},
        tags={"trigger_type": "on_demand", "requested_by": "test"},
    )

    assert result.success
    run_output = result.output_for_node("execute_ingest_run")
    run_id = str(run_output["run_id"])
    persisted = run_repo.fetch_run(run_id)
    assert persisted is not None
    assert persisted["run"]["run_id"] == run_id
    assert persisted["run"]["outcome_state"] in {"success", "partial_success", "failure"}
    assert int(persisted["run"]["due_source_count"]) >= 1
    assert int(persisted["run"]["executed_source_count"]) >= 1
    assert int(persisted["run"]["deferred_source_count"]) >= 0
    assert int(persisted["run"]["not_due_source_count"]) >= 0
    assert len(persisted["outcomes"]) >= 1
    assert len(persisted["eligibility"]) >= 1

    fred_outcomes = [
        row for row in persisted["outcomes"] if row["source_key"] == FRED_FEDFUNDS_SOURCE_KEY
    ]
    assert len(fred_outcomes) == 1
    assert int(fred_outcomes[0]["accepted_count"]) >= 0


def test_ingest_job_persists_deferred_counts_when_sources_are_carried_forward() -> None:
    """Run summary should persist deferred due sources when overlap guard blocks launch."""
    runtime = get_ingest_runtime()
    run_repo = runtime.run_repository

    probe_run_id = f"run-probe-{uuid4()}"
    try:
        run_repo.fetch_run(probe_run_id)
    except Exception as exc:  # pragma: no cover - environment-dependent integration guard
        pytest.skip(f"postgres runtime DB unavailable for integration test: {exc}")

    run_repo.clear_all()
    runtime.source_lock_service.acquire(FRED_FEDFUNDS_SOURCE_KEY, "active-token")
    runtime.source_lock_service.acquire(FRED_FEDFUNDS_SOURCE_KEY, "queued-token")

    try:
        result = defs.get_job_def("ingest_job").execute_in_process(
            run_config={},
            tags={"trigger_type": "scheduled", "requested_by": "carry-forward-test"},
        )

        assert result.success
        run_output = result.output_for_node("execute_ingest_run")
        persisted = run_repo.fetch_run(str(run_output["run_id"]))
        assert persisted is not None
        assert int(persisted["run"]["deferred_source_count"]) >= 1
    finally:
        runtime.source_lock_service.release(FRED_FEDFUNDS_SOURCE_KEY, "active-token")
        runtime.source_lock_service.release(FRED_FEDFUNDS_SOURCE_KEY, "queued-token")


def test_ingest_job_persists_schedule_policy_rows_for_registered_sources() -> None:
    """Successful ingest run should persist schedule state for registered sources."""
    if not os.getenv("FRED_API_KEY", "").strip():
        pytest.skip("FRED_API_KEY not set; skipping schedule policy persistence integration")

    runtime = get_ingest_runtime()
    run_repo = runtime.run_repository

    probe_run_id = f"run-probe-{uuid4()}"
    try:
        run_repo.fetch_run(probe_run_id)
    except Exception as exc:  # pragma: no cover - environment-dependent integration guard
        pytest.skip(f"postgres runtime DB unavailable for integration test: {exc}")

    run_repo.clear_all()

    result = defs.get_job_def("ingest_job").execute_in_process(
        run_config={},
        tags={"trigger_type": "on_demand", "requested_by": "schedule-policy-test"},
    )

    assert result.success

    rows = run_repo.read_all_schedule_policies()

    assert rows
    for row in rows.values():
        assert row["last_successful_at"] is not None


def test_ingest_job_reports_fred_source_outcome_visibility() -> None:
    """Run output should include a row for the FRED source outcome."""
    if not os.getenv("FRED_API_KEY", "").strip():
        pytest.skip(
            "FRED_API_KEY not set; skipping live FRED source outcome visibility integration"
        )

    runtime = get_ingest_runtime()
    run_repo = runtime.run_repository

    probe_run_id = f"run-probe-{uuid4()}"
    try:
        run_repo.fetch_run(probe_run_id)
    except Exception as exc:  # pragma: no cover - environment-dependent integration guard
        pytest.skip(f"postgres runtime DB unavailable for integration test: {exc}")

    run_repo.clear_all()

    result = defs.get_job_def("ingest_job").execute_in_process(
        run_config={},
        tags={"trigger_type": "on_demand", "requested_by": "fred-outcome-visibility"},
    )

    assert result.success
    run_output = result.output_for_node("execute_ingest_run")
    persisted = run_repo.fetch_run(str(run_output["run_id"]))
    assert persisted is not None

    source_keys = {str(row["source_key"]) for row in persisted["outcomes"]}
    assert FRED_FEDFUNDS_SOURCE_KEY in source_keys


def test_ingest_job_series_targeted_request_executes_selected_series_only() -> None:
    """Series-targeted trigger should execute selected series item without unrelated slices."""
    if not os.getenv("FRED_API_KEY", "").strip():
        pytest.skip("FRED_API_KEY not set; skipping live FRED series-targeted ingest integration")

    runtime = get_ingest_runtime()
    run_repo = runtime.run_repository

    probe_run_id = f"run-probe-{uuid4()}"
    try:
        run_repo.fetch_run(probe_run_id)
    except Exception as exc:  # pragma: no cover - environment-dependent integration guard
        pytest.skip(f"postgres runtime DB unavailable for integration test: {exc}")

    run_repo.clear_all()

    result = defs.get_job_def("ingest_job").execute_in_process(
        run_config={},
        tags={
            "trigger_type": "on_demand",
            "requested_by": "series-target-test",
            "series_item_key": "fred_fedfunds",
        },
    )

    assert result.success
    run_output = result.output_for_node("execute_ingest_run")
    source_rows = [
        row for row in run_output["source_results"] if row["source_key"] == FRED_FEDFUNDS_SOURCE_KEY
    ]
    assert len(source_rows) == 1
    series_outcomes = source_rows[0].get("series_outcomes", [])
    assert isinstance(series_outcomes, list)
    if series_outcomes:
        series_item_keys = {
            str(outcome["series_item_key"])
            for outcome in series_outcomes
            if "series_item_key" in outcome
        }
        assert series_item_keys <= {"fred_fedfunds"}


def test_ingest_job_second_run_adds_no_duplicate_fred_observations() -> None:
    """Two immediate runs should not create duplicate FRED observations."""
    if not os.getenv("FRED_API_KEY", "").strip():
        pytest.skip("FRED_API_KEY not set; skipping live FRED duplicate-check integration")

    runtime = get_ingest_runtime()
    run_repo = runtime.run_repository
    observation_repo = PostgresObservationRepository()

    probe_run_id = f"run-probe-{uuid4()}"
    try:
        run_repo.fetch_run(probe_run_id)
        observation_repo.read_latest_observed_on(series_key="INT.US.FEDFUNDS")
    except Exception as exc:  # pragma: no cover - environment-dependent integration guard
        pytest.skip(f"postgres runtime DB unavailable for integration test: {exc}")

    run_repo.clear_all()
    observation_repo.clear_all()

    first = defs.get_job_def("ingest_job").execute_in_process(
        run_config={},
        tags={"trigger_type": "on_demand", "requested_by": "fred-dup-check-first"},
    )
    assert first.success
    after_first = observation_repo.read_series_observations(series_key="INT.US.FEDFUNDS")

    second = defs.get_job_def("ingest_job").execute_in_process(
        run_config={},
        tags={"trigger_type": "on_demand", "requested_by": "fred-dup-check-second"},
    )
    assert second.success
    after_second = observation_repo.read_series_observations(series_key="INT.US.FEDFUNDS")

    assert len(after_second) == len(after_first)


def test_dagit_start_helper_reports_ready_for_existing_live_pid() -> None:
    """Startup helper should report ready when a live pid file already exists."""
    repo_root = Path(__file__).resolve().parents[4]
    tmp_dir = repo_root / ".tmp"
    pid_file = tmp_dir / "dagit-local.pid"

    tmp_dir.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(f"{os.getpid()}\n", encoding="utf-8")

    try:
        completed = subprocess.run(
            ["bash", "tools/quality/local-stack/start-dagit-local.sh"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )

        assert completed.returncode == 0
        assert "DAGIT_START_STATUS=ready" in completed.stdout
    finally:
        pid_file.unlink(missing_ok=True)


def test_definitions_detail_navigation_readiness_for_ingest_job() -> None:
    """Definitions should expose ingest job detail metadata for Dagit detail views."""
    ingest_def = defs.get_job_def("ingest_job")
    node_names = {node.name for node in ingest_def.graph.node_defs}

    assert ingest_def.name == "ingest_job"
    assert "execute_ingest_run" in node_names


def test_workspace_load_failure_category_mapping() -> None:
    """Workspace mismatch should map to workspace_load_failed category."""
    assert (
        map_dagit_failure_category(
            prerequisites_ready=True,
            endpoint_reachable=True,
            workspace_loaded=False,
        )
        == "workspace_load_failed"
    )


def test_partial_environment_failure_category_mapping() -> None:
    """Degraded state fallback should map to partial_environment category."""
    assert (
        map_dagit_failure_category(
            prerequisites_ready=True,
            endpoint_reachable=True,
            workspace_loaded=True,
        )
        == "partial_environment"
    )


def test_ingest_runtime_exposes_dagster_only_scheduling_authority() -> None:
    """Runtime should expose Dagster-only scheduling authority state after cutover."""
    runtime = get_ingest_runtime()

    assert runtime.authority_state.authority_mode == "dagster_only"
    assert runtime.authority_state.legacy_paths_disabled is True


def test_no_shared_schedule_trigger_path_in_definitions() -> None:
    """Feature 011 US3: no shared all-source schedule should exist in definitions."""
    schedule_names = {s.name for s in (defs.schedules or [])}
    assert "ingest_schedule" not in schedule_names
    # Verify active source schedules are present instead.
    assert "fred_fedfunds_schedule" in schedule_names
