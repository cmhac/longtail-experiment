"""US1 tests for trend signature comparison helpers."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_signature import TrendSignature, signatures_match


def test_signatures_match_for_identical_dimensions() -> None:
    """Matching label/direction/strength/seasonality should compare equal."""
    left = TrendSignature(
        trend_label="mild_sustained_uptrend",
        direction="up",
        strength="mild",
        seasonality_classification="non_seasonal",
    )
    right = TrendSignature(
        trend_label="mild_sustained_uptrend",
        direction="up",
        strength="mild",
        seasonality_classification="non_seasonal",
    )

    assert signatures_match(left=left, right=right)


def test_signatures_do_not_match_when_any_dimension_changes() -> None:
    """Any single signature field change should break continuity match."""
    base = TrendSignature(
        trend_label="mild_sustained_uptrend",
        direction="up",
        strength="mild",
        seasonality_classification="non_seasonal",
    )
    changed = TrendSignature(
        trend_label="mild_sustained_uptrend",
        direction="up",
        strength="mild",
        seasonality_classification="seasonal",
    )

    assert not signatures_match(left=base, right=changed)
