"""US1 tests for cadence inference and explicit cadence failures."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from trend_analysis.cadence import (
    DOMINANT_CADENCE_REQUIRED,
    MAX_IRREGULAR_GAP_RATIO,
    SUPPORTED_CADENCE_FAMILIES,
    CadenceInferenceError,
    infer_cadence,
    infer_cadence_decision,
)

from .fixtures.trend_series_fixtures import make_linear_series

MAX_IRREGULAR_GAP_RATIO_CONTRACT = 0.002
INTERVAL_COUNT_AT_THRESHOLD = 500


def test_infer_cadence_monthly_from_regular_spacing() -> None:
    """Regular month-spaced samples should infer monthly cadence."""
    points = make_linear_series(
        start=date(2023, 1, 1),
        values=[1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6],
    )

    cadence = infer_cadence([(point.period, point.value) for point in points])

    assert cadence == "monthly"


def test_infer_cadence_fails_for_irregular_spacing() -> None:
    """Mixed spacing that cannot map to one cadence should fail explicitly."""
    observations = [
        (date(2024, 1, 1), 10.0),
        (date(2024, 1, 8), 10.1),
        (date(2024, 2, 1), 10.2),
        (date(2024, 2, 9), 10.3),
        (date(2024, 3, 1), 10.4),
    ]

    with pytest.raises(CadenceInferenceError, match="cannot be inferred"):
        infer_cadence(observations)


def _daily_observations_with_one_large_gap(*, interval_count: int) -> list[tuple[date, float]]:
    day = date(2024, 1, 1)
    observations: list[tuple[date, float]] = [(day, 100.0)]
    gap_index = interval_count // 2
    for index in range(interval_count):
        day += timedelta(days=10 if index == gap_index else 1)
        observations.append((day, 100.0 + float(index + 1)))
    return observations


def test_cadence_policy_constants_match_contract_baseline() -> None:
    """Cadence policy constants should remain aligned with feature contract values."""
    assert MAX_IRREGULAR_GAP_RATIO == MAX_IRREGULAR_GAP_RATIO_CONTRACT
    assert DOMINANT_CADENCE_REQUIRED is True
    assert SUPPORTED_CADENCE_FAMILIES == ("daily", "weekly", "monthly")


def test_infer_cadence_accepts_isolated_gap_at_threshold() -> None:
    """One isolated irregular gap at threshold should be accepted as gap_tolerant."""
    observations = _daily_observations_with_one_large_gap(
        interval_count=INTERVAL_COUNT_AT_THRESHOLD
    )

    decision = infer_cadence_decision(observations)

    assert decision.cadence_state == "gap_tolerant"
    assert decision.inferred_cadence == "daily"
    assert decision.irregular_gap_count == 1
    assert decision.total_interval_count == INTERVAL_COUNT_AT_THRESHOLD
    assert decision.irregular_gap_ratio == MAX_IRREGULAR_GAP_RATIO
    assert decision.reason_code == "isolated_irregular_gaps_tolerated"
    assert infer_cadence(observations) == "daily"


def test_infer_cadence_rejects_persistent_irregular_ratio_over_threshold() -> None:
    """Higher irregular-gap ratios should remain explicitly rejected."""
    observations = [
        (date(2024, 1, 1), 100.0),
        (date(2024, 1, 2), 101.0),
        (date(2024, 1, 3), 102.0),
        (date(2024, 1, 4), 103.0),
        (date(2024, 1, 5), 104.0),
        (date(2024, 1, 15), 105.0),
    ]

    decision = infer_cadence_decision(observations)

    assert decision.cadence_state == "irregular_rejected"
    assert decision.inferred_cadence is None
    assert decision.reason_code == "irregular_gap_ratio_exceeds_threshold"
    with pytest.raises(CadenceInferenceError, match="irregular_gap_ratio_exceeds_threshold"):
        infer_cadence(observations)


def test_infer_cadence_rejects_mixed_cadence_families_even_with_tolerable_gaps() -> None:
    """Mixed supported cadence families should still be rejected deterministically."""
    observations = [
        (date(2024, 1, 1), 100.0),
        (date(2024, 1, 2), 101.0),
        (date(2024, 1, 3), 102.0),
        (date(2024, 1, 10), 103.0),
        (date(2024, 1, 11), 104.0),
    ]

    decision = infer_cadence_decision(observations)

    assert decision.cadence_state == "irregular_rejected"
    assert decision.reason_code == "mixed_cadence_families"
    with pytest.raises(CadenceInferenceError, match="mixed_cadence_families"):
        infer_cadence(observations)


def test_infer_cadence_preserves_non_increasing_period_failure() -> None:
    """Non-increasing periods should preserve explicit hard-failure behavior."""
    observations = [
        (date(2024, 1, 1), 100.0),
        (date(2024, 1, 2), 101.0),
        (date(2024, 1, 2), 102.0),
    ]

    decision = infer_cadence_decision(observations)

    assert decision.cadence_state == "irregular_rejected"
    assert decision.reason_code == "non_increasing_periods"
    with pytest.raises(CadenceInferenceError, match="non-increasing periods"):
        infer_cadence(observations)


def test_infer_cadence_decision_is_deterministic_for_identical_inputs() -> None:
    """Identical observations should produce identical cadence decisions."""
    observations = _daily_observations_with_one_large_gap(interval_count=500)

    first = infer_cadence_decision(observations)
    second = infer_cadence_decision(observations)

    assert first == second
