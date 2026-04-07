"""US1 canonical arbitration tests for v2 weighting and flat support."""

from __future__ import annotations

from datetime import date

from trend_analysis import evaluate_multi_lookbacks


def test_arbitration_returns_available_for_directional_series() -> None:
    observations = [
        ("2026-01-01", 100.0),
        ("2026-01-02", 102.0),
        ("2026-01-03", 105.0),
        ("2026-01-04", 109.0),
        ("2026-01-05", 114.0),
        ("2026-01-06", 120.0),
    ]
    result = evaluate_multi_lookbacks([(date.fromisoformat(d), v) for d, v in observations])

    assert result.canonical_descriptor.descriptor_state == "available"
    assert result.canonical_descriptor.direction in {"up", "down", "flat"}


def test_arbitration_returns_unavailable_when_no_snapshots() -> None:
    result = evaluate_multi_lookbacks([])
    assert result.canonical_descriptor.descriptor_state == "unavailable"
