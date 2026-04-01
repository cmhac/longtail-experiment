"""US1 prototype-guided regression scenarios for real-series-like inputs."""

from __future__ import annotations

from datetime import date

from trend_analysis.classifier import analyze_series

from .fixtures.trend_series_fixtures import make_linear_series


def test_real_series_like_uptrend_classifies_as_significant() -> None:
    """A sustained upward sequence should classify as a significant trend."""
    points = make_linear_series(
        start=date(2024, 1, 1),
        values=[3.10, 3.20, 3.30, 3.45, 3.60, 3.75, 3.95, 4.10, 4.35, 4.55],
    )
    result = analyze_series([(point.period, point.value) for point in points])

    assert result.outcome == "significant_trend"
    assert result.signature is not None
    assert result.signature.direction == "up"


def test_real_series_like_flattened_sequence_is_no_significant_trend() -> None:
    """Near-flat noisy values should resolve to a no-significant no-op outcome."""
    points = make_linear_series(
        start=date(2024, 1, 1),
        values=[4.10, 4.12, 4.11, 4.13, 4.12, 4.10, 4.14, 4.11],
    )
    result = analyze_series([(point.period, point.value) for point in points])

    assert result.outcome == "no_significant_trend"
    assert result.signature is None
