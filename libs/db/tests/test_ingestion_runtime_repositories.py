"""Repository unit tests for runtime outcomes and conflicts."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from db.repositories.conflict_repository import (
    InMemoryConflictRepository,
    StoredConflict,
)
from db.repositories.run_repository import InMemoryRunRepository, StoredRunOutcome


def test_run_repository_round_trip() -> None:
    repo = InMemoryRunRepository()
    row = StoredRunOutcome(
        run_id="run-001",
        trigger_type="scheduled",
        outcome_state="partial_success",
        accepted_count=10,
        quarantined_count=2,
        failed_count=1,
        duplicate_no_op_count=3,
        conflict_count=1,
    )

    repo.add_run_outcome(row)

    assert repo.get_run_outcome("run-001") == row


def test_conflict_repository_filters_by_run() -> None:
    repo = InMemoryConflictRepository()
    c1 = StoredConflict(
        conflict_id="conf-1",
        run_id="run-001",
        source_key="bls",
        series_key="CPI.US.ALL",
        reference_period_key="2026-01",
        existing_observation_ref="obs-old",
        incoming_record_ref="rec-new",
        conflict_type="value_mismatch",
        conflict_state="open",
    )
    c2 = StoredConflict(
        conflict_id="conf-2",
        run_id="run-002",
        source_key="bls",
        series_key="CPI.US.ALL",
        reference_period_key="2026-02",
        existing_observation_ref="obs-old-2",
        incoming_record_ref="rec-new-2",
        conflict_type="value_mismatch",
        conflict_state="open",
    )

    repo.add_conflict(c1)
    repo.add_conflict(c2)

    assert repo.list_conflicts("run-001") == [c1]
    assert set(repo.list_conflicts()) == {c1, c2}
