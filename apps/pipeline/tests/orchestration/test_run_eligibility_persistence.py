"""US2 persistence test for run eligibility snapshots."""

from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.definitions import defs, get_ingest_runtime


def test_eligibility_snapshots_are_persisted_for_each_run() -> None:
    """Ingest runs should persist per-source eligibility snapshots with reason codes."""
    runtime = get_ingest_runtime()
    run_repo = runtime.run_repository

    probe_run_id = f"eligibility-probe-{uuid4()}"
    try:
        run_repo.read_eligibility_snapshots(probe_run_id)
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"postgres runtime DB unavailable for eligibility persistence test: {exc}")

    result = defs.get_job_def("ingest_job").execute_in_process(
        run_config={},
        tags={"trigger_type": "scheduled", "requested_by": "eligibility-test"},
    )

    assert result.success
    output = result.output_for_node("execute_ingest_run")
    run_id = str(output["run_id"])
    snapshots = run_repo.read_eligibility_snapshots(run_id)

    assert snapshots
    assert {snapshot["source_key"] for snapshot in snapshots} >= {"fred_fedfunds"}
    for snapshot in snapshots:
        assert snapshot["eligibility_state"] in {
            "due",
            "not_due",
            "skipped_inactive",
            "skipped_invalid_policy",
        }
        assert isinstance(snapshot["selected_for_execution"], bool)
