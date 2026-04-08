"""US1 tests for deterministic canonical descriptor weighting behavior."""

from __future__ import annotations

from datetime import date

from trend_analysis import compute_canonical_descriptor, evaluate_multi_lookbacks
from trend_analysis.version import CANONICAL_WEIGHTING_VERSION

from .fixtures.trend_series_fixtures import make_linear_series


def _daily_points(values: list[float]) -> list[tuple[date, float]]:
    points = make_linear_series(start=date(2026, 1, 1), values=values)
    return [(point.period, point.value) for point in points]


def test_canonical_descriptor_prefers_recent_strong_signal() -> None:
    """Weighting should select the most informative recent significant lookback."""
    points = _daily_points([100.0, 102.0, 104.0, 107.0, 111.0, 116.0, 122.0, 129.0])
    result = evaluate_multi_lookbacks(points)

    canonical = result.canonical_descriptor
    assert canonical.descriptor_state == "available"
    assert canonical.selected_lookback_points == 2
    assert canonical.direction == "up"
    assert canonical.weighting_version == CANONICAL_WEIGHTING_VERSION


def test_canonical_descriptor_unavailable_when_no_significant_signals() -> None:
    """Canonical descriptor should be unavailable when all applicable lookbacks are no-signal."""
    points = _daily_points([100.0, 100.1, 100.0, 100.1, 100.0, 100.1, 100.0, 100.1])
    result = evaluate_multi_lookbacks(points)

    canonical = result.canonical_descriptor
    assert canonical.descriptor_state == "unavailable"
    assert canonical.selected_lookback_points is None
    assert canonical.reason_code == "no_significant_trend"


def test_canonical_weighting_is_deterministic_for_same_snapshots() -> None:
    """Direct weighting calculation should remain deterministic on repeated calls."""
    points = _daily_points([100.0, 102.0, 104.0, 106.5, 109.0, 112.5, 116.0, 120.0])
    snapshots = evaluate_multi_lookbacks(points).lookback_snapshots

    first = compute_canonical_descriptor(snapshots)
    second = compute_canonical_descriptor(snapshots)

    assert first == second
