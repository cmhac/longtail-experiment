"""Deterministic trend classification with library-owned defaults."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import Literal

from .cadence import infer_cadence
from .models import TrendAnalysisResult, TrendSignature, build_result

MIN_REQUIRED_OBSERVATIONS = 6
SIGNIFICANT_RELATIVE_CHANGE = 0.05
STRONG_RELATIVE_CHANGE = 0.10
EPSILON = 1e-9
SEASONAL_MIN_MONTHLY_OBSERVATIONS = 24


def _relative_change(start_value: float, end_value: float) -> float:
    baseline = abs(start_value) if abs(start_value) > EPSILON else 1.0
    return (end_value - start_value) / baseline


def _seasonality_classification(
    *,
    cadence: str,
    observation_count: int,
) -> Literal["seasonal", "non_seasonal"]:
    # Deterministic heuristic: only monthly series with >=24 points are seasonal.
    if cadence == "monthly" and observation_count >= SEASONAL_MIN_MONTHLY_OBSERVATIONS:
        return "seasonal"
    return "non_seasonal"


def _trend_label(direction: str, strength: str) -> str:
    if direction == "up" and strength == "strong":
        return "strong_sustained_uptrend"
    if direction == "up" and strength == "mild":
        return "mild_sustained_uptrend"
    if direction == "down" and strength == "strong":
        return "strong_sustained_downtrend"
    return "mild_sustained_downtrend"


def analyze_series(observations: Sequence[tuple[date, float]]) -> TrendAnalysisResult:
    """Analyze one ordered observation series and return deterministic outcome."""
    if len(observations) < MIN_REQUIRED_OBSERVATIONS:
        return build_result(
            outcome="insufficient_data",
            signature=None,
            start_period=None,
            end_period=None,
            reason="requires at least 6 observations",
        )

    cadence = infer_cadence(observations)
    first_period, first_value = observations[0]
    last_period, last_value = observations[-1]

    change_ratio = _relative_change(first_value, last_value)
    absolute_change_ratio = abs(change_ratio)
    if absolute_change_ratio < SIGNIFICANT_RELATIVE_CHANGE:
        return build_result(
            outcome="no_significant_trend",
            signature=None,
            start_period=first_period,
            end_period=last_period,
            reason="change remains below significant threshold",
        )

    direction = "up" if change_ratio > 0 else "down"
    strength = "strong" if absolute_change_ratio >= STRONG_RELATIVE_CHANGE else "mild"
    seasonality = _seasonality_classification(
        cadence=cadence,
        observation_count=len(observations),
    )
    signature = TrendSignature(
        trend_label=_trend_label(direction, strength),
        direction=direction,
        strength=strength,
        seasonality_classification=seasonality,
    )

    return build_result(
        outcome="significant_trend",
        signature=signature,
        start_period=first_period,
        end_period=last_period,
        reason=f"{cadence} cadence with {direction} {strength} movement",
    )
