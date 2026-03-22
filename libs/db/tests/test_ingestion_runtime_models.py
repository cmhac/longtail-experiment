"""Model-level tests for schedule policy and eligibility runtime entities."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from db.models import SourceEligibilitySnapshot, SourceSchedulePolicy


def test_schedule_policy_model_metadata() -> None:
    """Schedule policy table metadata should expose expected table and key columns."""
    table = SourceSchedulePolicy.__table__

    assert SourceSchedulePolicy.__tablename__ == "source_schedule_policies"
    assert "source_key" in table.columns
    assert table.columns["source_key"].nullable is False
    assert table.columns["cadence_type"].nullable is False


def test_eligibility_snapshot_model_metadata() -> None:
    """Eligibility snapshot model should enforce run+source uniqueness."""
    table = SourceEligibilitySnapshot.__table__

    assert SourceEligibilitySnapshot.__tablename__ == "source_eligibility_snapshots"
    assert "run_id" in table.columns
    assert "source_key" in table.columns

    unique_names = {constraint.name for constraint in table.constraints if constraint.name}
    assert "uq_eligibility_run_source" in unique_names
