"""US1 scoring tests for Theil-Sen + Kendall confidence modifiers."""

from __future__ import annotations

from trend_analysis.scoring import score_window


def test_theilsen_kendall_scores_uptrend_with_high_confidence() -> None:
    score = score_window([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])

    assert score.direction == "up"
    assert score.confidence_score >= 0.7
    assert score.theil_sen_slope > 0


def test_theilsen_kendall_scores_flat_when_low_signal() -> None:
    score = score_window([10.0, 10.1, 9.9, 10.0, 10.1, 9.9])

    assert score.direction == "flat"
    assert score.confidence_score < 0.5
