"""US1 tests for terminal trend-analysis outcomes."""

from __future__ import annotations

from datetime import date

from trend_analysis.classifier import analyze_series

from .fixtures.trend_series_fixtures import make_linear_series


def test_insufficient_data_outcome_skips_lifecycle_writes() -> None:
    """Series below minimum observation threshold should return insufficient_data."""
    points = make_linear_series(
        start=date(2025, 1, 1),
        values=[100.0, 101.0, 102.0, 103.0, 104.0],
    )

    result = analyze_series([(point.period, point.value) for point in points])

    assert result.outcome == "insufficient_data"
    assert result.signature is None


def test_no_significant_trend_outcome_for_flat_series() -> None:
    """Low-variance flat sequences should produce a no_significant_trend outcome."""
    points = make_linear_series(
        start=date(2024, 1, 1),
        values=[100.0, 100.1, 100.0, 100.2, 100.1, 100.0, 100.2, 100.1],
    )

    result = analyze_series([(point.period, point.value) for point in points])

    assert result.outcome == "no_significant_trend"
    assert result.signature is None


def test_runtime_env_overrides_do_not_change_library_defaults(monkeypatch) -> None:
    """Environment overrides must not influence hardcoded library thresholds."""
    points = make_linear_series(
        start=date(2024, 1, 1),
        values=[100.0, 101.0, 102.5, 104.5, 106.5, 108.8, 111.2, 114.0],
    )
    observations = [(point.period, point.value) for point in points]

    baseline = analyze_series(observations)

    monkeypatch.setenv("LONGTAIL_TREND_THRESHOLD", "0.000001")
    monkeypatch.setenv("LONGTAIL_TREND_CADENCE_WINDOW", "999")
    monkeypatch.setenv("LONGTAIL_TREND_SEASONALITY_WINDOW", "999")

    with_overrides = analyze_series(observations)

    assert baseline == with_overrides
