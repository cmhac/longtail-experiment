"""Backfill decision helpers for trend lifecycle processing."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_ANALYSIS_VERSION = "0.1.0"
LOOKBACK_RECLASSIFICATION_REASON = "lookback_snapshot_reclassification"


@dataclass(frozen=True)
class TrendBackfillDecision:
    """Decision result for backfill/rerun planning in trend processing."""

    run_full_backfill: bool
    reason: str


def decide_backfill_scope(
    *,
    existing_trend_record_count: int,
    has_sufficient_history: bool,
) -> TrendBackfillDecision:
    """Decide first-run full-history backfill eligibility for one series."""
    if existing_trend_record_count == 0 and has_sufficient_history:
        return TrendBackfillDecision(run_full_backfill=True, reason="first_run_full_backfill")
    if existing_trend_record_count == 0 and not has_sufficient_history:
        return TrendBackfillDecision(
            run_full_backfill=False,
            reason="insufficient_history_forward_only",
        )
    return TrendBackfillDecision(run_full_backfill=False, reason="existing_trends_forward_only")


def requires_global_rerun_for_library_release(
    *,
    persisted_analysis_version: str | None,
    current_library_version: str = DEFAULT_ANALYSIS_VERSION,
) -> bool:
    """Return whether a series requires operator-triggered full rerun/re-backfill."""
    if persisted_analysis_version is None:
        return False
    return persisted_analysis_version != current_library_version


def requires_lookback_reclassification_for_library_release(
    *,
    persisted_analysis_version: str | None,
    current_library_version: str = DEFAULT_ANALYSIS_VERSION,
) -> bool:
    """Return whether lookback snapshots require deterministic reclassification."""
    return requires_global_rerun_for_library_release(
        persisted_analysis_version=persisted_analysis_version,
        current_library_version=current_library_version,
    )
