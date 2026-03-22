"""Integration tests for Dagster ingest job runtime execution."""

from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.definitions import defs, get_ingest_runtime


def test_ingest_job_executes_and_creates_dummy_source_data() -> None:
    """Dagster ingest job should persist run and source outcome rows in Postgres."""
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
        tags={"trigger_type": "on_demand", "requested_by": "test"},
    )

    assert result.success
    run_output = result.output_for_node("execute_ingest_run")
    run_id = str(run_output["run_id"])
    persisted = run_repo.fetch_run(run_id)
    assert persisted is not None
    assert persisted["run"]["run_id"] == run_id
    assert persisted["run"]["outcome_state"] in {"success", "partial_success"}
    assert len(persisted["outcomes"]) >= 1

    dummy_outcomes = [row for row in persisted["outcomes"] if row["source_key"] == "dummy_source"]
    assert len(dummy_outcomes) == 1
    assert int(dummy_outcomes[0]["accepted_count"]) >= 1
