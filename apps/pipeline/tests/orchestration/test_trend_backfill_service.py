"""US1 tests for trend backfill decision behavior."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_backfill_service import (
    DEFAULT_ANALYSIS_VERSION,
    LOOKBACK_RECLASSIFICATION_REASON,
    decide_backfill_scope,
    requires_global_rerun_for_library_release,
    requires_lookback_reclassification_for_library_release,
)


def test_full_backfill_only_on_first_run_with_sufficient_history() -> None:
    """First run with sufficient history should trigger full historical backfill."""
    decision = decide_backfill_scope(
        existing_trend_record_count=0,
        has_sufficient_history=True,
    )

    assert decision.run_full_backfill is True
    assert decision.reason == "first_run_full_backfill"


def test_forward_only_when_no_history_is_insufficient() -> None:
    """First run without enough history should skip full backfill."""
    decision = decide_backfill_scope(
        existing_trend_record_count=0,
        has_sufficient_history=False,
    )

    assert decision.run_full_backfill is False
    assert decision.reason == "insufficient_history_forward_only"


def test_library_release_change_requires_global_rerun() -> None:
    """Persisted version drift should require explicit full rerun/re-backfill."""
    assert requires_global_rerun_for_library_release(
        persisted_analysis_version="0.0.1",
        current_library_version=DEFAULT_ANALYSIS_VERSION,
    )
    assert not requires_global_rerun_for_library_release(
        persisted_analysis_version=DEFAULT_ANALYSIS_VERSION,
        current_library_version=DEFAULT_ANALYSIS_VERSION,
    )


def test_lookback_reclassification_follows_analysis_version_drift() -> None:
    """Lookback snapshot reclassification should mirror release drift behavior."""
    assert LOOKBACK_RECLASSIFICATION_REASON == "lookback_snapshot_reclassification"
    assert requires_lookback_reclassification_for_library_release(
        persisted_analysis_version="0.0.1",
        current_library_version=DEFAULT_ANALYSIS_VERSION,
    )
    assert not requires_lookback_reclassification_for_library_release(
        persisted_analysis_version=DEFAULT_ANALYSIS_VERSION,
        current_library_version=DEFAULT_ANALYSIS_VERSION,
    )
