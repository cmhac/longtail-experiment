"""US1 regression tests for deterministic trend-analysis outputs."""

from __future__ import annotations

from datetime import date

from trend_analysis.classifier import analyze_series
from trend_analysis.models import TrendAnalysisResult

from .fixtures.trend_series_fixtures import make_linear_series


def _sample_uptrend() -> list[tuple[date, float]]:
    """Return a deterministic upward monthly series used by multiple tests."""
    points = make_linear_series(
        start=date(2024, 1, 1),
        values=[100.0, 102.0, 104.0, 106.0, 109.0, 112.0, 116.0, 121.0],
    )
    return [(point.period, point.value) for point in points]


def test_analyze_series_is_deterministic_for_identical_inputs() -> None:
    """Running analysis twice on identical inputs should produce the same output."""
    observations = _sample_uptrend()

    first: TrendAnalysisResult = analyze_series(observations)
    second: TrendAnalysisResult = analyze_series(observations)

    assert first == second
    assert first.analysis_version == second.analysis_version
    assert first.outcome == "significant_trend"
