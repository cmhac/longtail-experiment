"""Integration tests for Dagster ingest job runtime execution."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from uuid import uuid4

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.definitions import defs, get_ingest_runtime
from src.orchestration.jobs.sources.fred_fedfunds_source import FRED_FEDFUNDS_SOURCE_KEY
from src.orchestration.resources.postgres_observation_repository import (
    PostgresObservationRepository,
)


def test_ingest_job_executes_and_creates_dummy_source_data() -> None:
    """Dagster ingest job should persist run and source outcome rows in Postgres."""
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
    assert persisted["run"]["outcome_state"] in {"success", "partial_success"}
    assert int(persisted["run"]["due_source_count"]) >= 1
    assert int(persisted["run"]["executed_source_count"]) >= 1
    assert int(persisted["run"]["deferred_source_count"]) >= 0
    assert int(persisted["run"]["not_due_source_count"]) >= 0
    assert len(persisted["outcomes"]) >= 1
    assert len(persisted["eligibility"]) >= 1

    dummy_outcomes = [row for row in persisted["outcomes"] if row["source_key"] == "dummy_source"]
    assert len(dummy_outcomes) == 1
    assert int(dummy_outcomes[0]["accepted_count"]) >= 0


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
    runtime.source_lock_service.acquire("dummy_source", "active-token")
    runtime.source_lock_service.acquire("dummy_source", "queued-token")

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
        runtime.source_lock_service.release("dummy_source", "active-token")
        runtime.source_lock_service.release("dummy_source", "queued-token")


def test_ingest_job_persists_schedule_policy_rows_for_registered_sources() -> None:
    """Successful ingest run should persist schedule state for registered sources."""
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
