"""US1 tests for multi-lookback catalog and deterministic applicability outcomes."""

from __future__ import annotations

from datetime import date

from trend_analysis import LOOKBACK_CATALOG, evaluate_multi_lookbacks

from .fixtures.trend_series_fixtures import make_linear_series


def _daily_points(values: list[float]) -> list[tuple[date, float]]:
    points = make_linear_series(start=date(2026, 1, 1), values=values)
    return [(point.period, point.value) for point in points]


def test_catalog_matches_spec_fixed_values() -> None:
    """Library lookback catalog should remain fixed to spec contract values."""
    assert LOOKBACK_CATALOG == (1, 2, 3, 4, 5, 10, 25, 50, 100, 250, 500, 1000)


def test_evaluate_multi_lookbacks_marks_depth_inapplicable_with_reason() -> None:
    """Insufficient depth should produce explicit inapplicable applicability rows."""
    points = _daily_points([100.0, 101.0, 102.0, 103.0, 104.0, 105.0])

    result = evaluate_multi_lookbacks(points)
    by_lookback = {item.lookback_points: item for item in result.applicability}

    assert by_lookback[1].applicability_state == "applicable"
    assert by_lookback[5].applicability_state == "applicable"
    assert by_lookback[10].applicability_state == "inapplicable"
    assert by_lookback[10].reason_code == "insufficient_history"


def test_evaluate_multi_lookbacks_records_no_signal_for_flat_series() -> None:
    """Applicable lookbacks with small moves should persist no-significant states."""
    points = _daily_points([100.0, 100.1, 100.0, 100.1, 100.0, 100.1, 100.0, 100.1])

    result = evaluate_multi_lookbacks(points)
    snapshots = {item.lookback_points: item for item in result.lookback_snapshots}

    assert snapshots[1].outcome_state == "no_significant_trend"
    assert snapshots[2].outcome_state == "no_significant_trend"
    assert snapshots[5].outcome_state == "no_significant_trend"


def test_evaluate_multi_lookbacks_is_deterministic_for_identical_inputs() -> None:
    """Identical ordered observations should produce identical multi-lookback results."""
    points = _daily_points([100.0, 101.0, 102.0, 104.0, 107.0, 111.0, 116.0, 122.0])

    first = evaluate_multi_lookbacks(points)
    second = evaluate_multi_lookbacks(points)

    assert first == second
