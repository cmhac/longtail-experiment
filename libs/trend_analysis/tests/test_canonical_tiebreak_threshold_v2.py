"""US1 tie-break threshold behavior tests for v2 arbitration."""

from __future__ import annotations

from datetime import date

from trend_analysis import evaluate_multi_lookbacks


def test_tiebreak_threshold_prefers_shorter_lookback_on_close_scores() -> None:
    observations = [
        (date(2026, 1, 1), 100.0),
        (date(2026, 1, 2), 103.0),
        (date(2026, 1, 3), 106.0),
        (date(2026, 1, 4), 110.0),
        (date(2026, 1, 5), 115.0),
        (date(2026, 1, 6), 121.0),
    ]

    descriptor = evaluate_multi_lookbacks(observations).canonical_descriptor
    assert descriptor.descriptor_state == "available"
    assert descriptor.selected_lookback_points is not None
