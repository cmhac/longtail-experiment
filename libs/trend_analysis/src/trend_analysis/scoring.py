"""Robust v2 scoring primitives for trend windows."""

from __future__ import annotations

from dataclasses import dataclass

from scipy.stats import kendalltau, theilslopes

_MIN_CONFIDENCE_THRESHOLD = 0.60
_MIN_RELATIVE_SLOPE_THRESHOLD = 0.005


@dataclass(frozen=True)
class TrendScore:
    """Result of scoring one observation window with Theil-Sen + Kendall."""

    direction: str
    confidence_score: float
    theil_sen_slope: float
    theil_sen_low_slope: float
    theil_sen_high_slope: float
    kendall_tau: float
    kendall_pvalue: float


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, value))


def score_window(values: list[float]) -> TrendScore:
    """Score one window with Theil-Sen slope and Kendall monotonic evidence."""
    x = list(range(len(values)))
    slope, _intercept, low_slope, high_slope = theilslopes(values, x)
    tau, pvalue = kendalltau(x, values)
    tau_value = 0.0 if tau is None else float(tau)
    pvalue_value = 1.0 if pvalue is None else float(pvalue)

    monotonic_strength = abs(tau_value)
    significance_weight = _bounded(1.0 - pvalue_value)
    slope_value = float(slope)
    low_slope_value = float(low_slope)
    high_slope_value = float(high_slope)
    baseline = max(abs(sum(values) / len(values)), 1e-8)
    relative_slope = abs(slope_value) / baseline

    slope_weight = _bounded(min(abs(slope_value), 1.0))
    confidence = _bounded(
        (0.5 * monotonic_strength) + (0.35 * significance_weight) + (0.15 * slope_weight)
    )

    if confidence < _MIN_CONFIDENCE_THRESHOLD or relative_slope < _MIN_RELATIVE_SLOPE_THRESHOLD:
        direction = "flat"
    else:
        direction = "up" if slope_value > 0 else "down"

    return TrendScore(
        direction=direction,
        confidence_score=confidence,
        theil_sen_slope=slope_value,
        theil_sen_low_slope=low_slope_value,
        theil_sen_high_slope=high_slope_value,
        kendall_tau=tau_value,
        kendall_pvalue=pvalue_value,
    )
