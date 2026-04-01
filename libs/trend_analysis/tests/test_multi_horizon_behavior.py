"""US1 prototype-guided multi-horizon regression scenarios."""

from __future__ import annotations

from datetime import date

from trend_analysis.classifier import analyze_series

from .fixtures.trend_series_fixtures import make_linear_series


def test_long_horizon_uptrend_stays_significant() -> None:
    """Long-horizon upward movement should remain a significant trend."""
    points = make_linear_series(
        start=date(2023, 1, 1),
        values=[
            100.0,
            101.0,
            102.0,
            103.2,
            104.5,
            105.8,
            107.2,
            108.7,
            110.3,
            112.0,
            113.8,
            115.7,
        ],
    )
    result = analyze_series([(point.period, point.value) for point in points])

    assert result.outcome == "significant_trend"
    assert result.signature is not None
    assert result.signature.strength in {"mild", "strong"}


def test_short_horizon_with_insufficient_points_is_terminal_no_write() -> None:
    """Multi-horizon short sequences should return insufficient_data terminal outcome."""
    points = make_linear_series(
        start=date(2025, 1, 1),
        values=[10.0, 10.2, 10.4, 10.8, 11.0],
    )
    result = analyze_series([(point.period, point.value) for point in points])

    assert result.outcome == "insufficient_data"
    assert result.signature is None
