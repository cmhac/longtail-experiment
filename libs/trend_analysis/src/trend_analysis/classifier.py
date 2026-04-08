"""Deterministic trend classification with library-owned defaults."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import Literal

from .cadence import CadenceInferenceError, infer_cadence, infer_cadence_decision
from .arbitration import compute_canonical_descriptor_v2
from .models import (
    OlsDiagnostics,
    PreprocessingMetadata,
    CanonicalTrendDescriptorResult,
    LookbackTrendSnapshotResult,
    MultiLookbackEvaluationResult,
    TrendAnalysisResult,
    TrendSignature,
    build_cadence_decision_result,
    build_canonical_descriptor,
    build_lookback_applicability_result,
    build_lookback_snapshot_result,
    build_result,
)
from .preprocessing import apply_ewma
from .scoring import score_window
from .seasonal_adjustment import seasonal_method_for_cadence

MIN_REQUIRED_OBSERVATIONS = 6
SIGNIFICANT_RELATIVE_CHANGE = 0.05
STRONG_RELATIVE_CHANGE = 0.10
EPSILON = 1e-9
SEASONAL_MIN_MONTHLY_OBSERVATIONS = 24
MAX_ANALYSIS_POINTS_BY_CADENCE: dict[str, int] = {
    "daily": 180,
    "weekly": 156,
    "monthly": 120,
}
LOOKBACK_CATALOG: tuple[int, ...] = (1, 2, 3, 4, 5, 10, 25, 50, 100, 250, 500, 1000)
MAX_LOOKBACK_BY_CADENCE: dict[str, int] = {
    "daily": 1000,
    "weekly": 500,
    "monthly": 250,
}
STRENGTH_WEIGHT_MULTIPLIER: dict[str, float] = {"mild": 1.0, "strong": 2.0}
MIN_LOOKBACK_OBSERVATION_COUNT = 2


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


def _analysis_window(
    observations: Sequence[tuple[date, float]],
    *,
    cadence: str,
) -> Sequence[tuple[date, float]]:
    window_size = MAX_ANALYSIS_POINTS_BY_CADENCE.get(cadence)
    if window_size is None or len(observations) <= window_size:
        return observations
    return observations[-window_size:]


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
    scoped_observations = _analysis_window(observations, cadence=cadence)
    first_period, first_value = scoped_observations[0]
    last_period, last_value = scoped_observations[-1]

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
        observation_count=len(scoped_observations),
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
        reason=(
            f"{cadence} cadence with {direction} {strength} movement "
            f"across {len(scoped_observations)} observations"
        ),
    )


def _lookback_relative_change(
    observations: Sequence[tuple[date, float]],
    *,
    lookback_points: int,
) -> float:
    reference_value = observations[-(lookback_points + 1)][1]
    latest_value = observations[-1][1]
    return _relative_change(reference_value, latest_value)


def _evaluate_lookback(
    observations: Sequence[tuple[date, float]],
    *,
    cadence: str,
    lookback_points: int,
) -> tuple[object, object | None]:
    if lookback_points >= len(observations):
        return (
            build_lookback_applicability_result(
                lookback_points=lookback_points,
                applicability_state="inapplicable",
                reason_code="insufficient_history",
                reason_detail=f"requires at least {lookback_points + 1} observations",
            ),
            None,
        )

    max_supported = MAX_LOOKBACK_BY_CADENCE[cadence]
    if lookback_points > max_supported:
        return (
            build_lookback_applicability_result(
                lookback_points=lookback_points,
                applicability_state="inapplicable",
                reason_code="cadence_lookback_not_supported",
                reason_detail=(
                    f"{cadence} cadence supports lookbacks up to {max_supported} observations"
                ),
            ),
            None,
        )

    window = observations[-(lookback_points + 1) :]
    smoothed_values, preprocessing = apply_ewma([point[1] for point in window])
    seasonal_method = seasonal_method_for_cadence(cadence)
    if seasonal_method != "none":
        preprocessing = PreprocessingMetadata(
            smoothing_method=preprocessing.smoothing_method,
            smoothing_parameters=preprocessing.smoothing_parameters,
            seasonal_adjustment_method=seasonal_method,
            seasonal_periods=(7,) if cadence == "weekly" else (12,),
            seasonal_reliability_state="reliable",
            preprocess_version=preprocessing.preprocess_version,
        )
    score = score_window(smoothed_values)

    if score.direction == "flat":
        snapshot = build_lookback_snapshot_result(
            lookback_points=lookback_points,
            outcome_state="no_significant_trend",
            descriptor_state="available",
            trend_label=None,
            direction="flat",
            confidence_score=score.confidence_score,
            dominant_measure_family="theil_sen",
            theil_sen_slope=score.theil_sen_slope,
            theil_sen_low_slope=score.theil_sen_low_slope,
            theil_sen_high_slope=score.theil_sen_high_slope,
            kendall_tau=score.kendall_tau,
            kendall_pvalue=score.kendall_pvalue,
            preprocessing=preprocessing,
            ols_diagnostics=OlsDiagnostics(
                slope=score.theil_sen_slope,
                intercept=window[0][1],
                r_squared=None,
                p_value=None,
            ),
            strength=None,
            seasonality_classification=None,
            reason_code="flat_signal",
            reason="change remains below significant threshold",
        )
    else:
        direction = score.direction
        magnitude = abs(score.theil_sen_slope)
        strength = "strong" if magnitude >= STRONG_RELATIVE_CHANGE else "mild"
        seasonality = _seasonality_classification(
            cadence=cadence,
            observation_count=lookback_points + 1,
        )
        snapshot = build_lookback_snapshot_result(
            lookback_points=lookback_points,
            outcome_state="significant_trend",
            descriptor_state="available",
            trend_label=_trend_label(direction, strength),
            direction=direction,
            confidence_score=score.confidence_score,
            dominant_measure_family="theil_sen",
            theil_sen_slope=score.theil_sen_slope,
            theil_sen_low_slope=score.theil_sen_low_slope,
            theil_sen_high_slope=score.theil_sen_high_slope,
            kendall_tau=score.kendall_tau,
            kendall_pvalue=score.kendall_pvalue,
            preprocessing=preprocessing,
            ols_diagnostics=OlsDiagnostics(
                slope=score.theil_sen_slope,
                intercept=window[0][1],
                r_squared=None,
                p_value=None,
            ),
            strength=strength,
            seasonality_classification=seasonality,
            reason_code=None,
            reason=f"{cadence} cadence evaluation over {lookback_points + 1} points",
        )

    return (
        build_lookback_applicability_result(
            lookback_points=lookback_points,
            applicability_state="applicable",
            reason_code="applicable",
            reason_detail=None,
        ),
        snapshot,
    )


def compute_canonical_descriptor(
    snapshots: Sequence[LookbackTrendSnapshotResult],
) -> CanonicalTrendDescriptorResult:
    """Compute deterministic canonical descriptor from lookback snapshot results."""
    return compute_canonical_descriptor_v2(list(snapshots))


def evaluate_multi_lookbacks(
    observations: Sequence[tuple[date, float]],
    *,
    lookback_catalog: Sequence[int] = LOOKBACK_CATALOG,
) -> MultiLookbackEvaluationResult:
    """Evaluate all lookbacks with applicability and canonical descriptor results."""
    if len(observations) < MIN_LOOKBACK_OBSERVATION_COUNT:
        empty_applicability = tuple(
            build_lookback_applicability_result(
                lookback_points=lookback,
                applicability_state="inapplicable",
                reason_code="insufficient_history",
                reason_detail=(f"requires at least {MIN_LOOKBACK_OBSERVATION_COUNT} observations"),
            )
            for lookback in lookback_catalog
        )
        return MultiLookbackEvaluationResult(
            analysis_version=build_result(
                outcome="insufficient_data",
                signature=None,
                start_period=None,
                end_period=None,
                reason=(f"requires at least {MIN_LOOKBACK_OBSERVATION_COUNT} observations"),
            ).analysis_version,
            weighting_version=build_canonical_descriptor(
                descriptor_state="unavailable",
                trend_label=None,
                direction=None,
                strength=None,
                selected_lookback_points=None,
                reason_code="insufficient_history",
                weighting_trace={"selected": None, "candidates": {}},
            ).weighting_version,
            evaluated_observation_count=len(observations),
            cadence_decision=build_cadence_decision_result(
                cadence_state="irregular_rejected",
                inferred_cadence=None,
                irregular_gap_count=0,
                total_interval_count=max(len(observations) - 1, 0),
                irregular_gap_ratio=0.0,
                reason_code="insufficient_history",
                reason_detail=(f"requires at least {MIN_LOOKBACK_OBSERVATION_COUNT} observations"),
            ),
            applicability=empty_applicability,
            lookback_snapshots=(),
            canonical_descriptor=build_canonical_descriptor(
                descriptor_state="unavailable",
                trend_label=None,
                direction=None,
                strength=None,
                selected_lookback_points=None,
                reason_code="insufficient_history",
                weighting_trace={"selected": None, "candidates": {}},
            ),
        )

    cadence_decision = infer_cadence_decision(observations)
    cadence = cadence_decision.inferred_cadence
    if cadence_decision.cadence_state == "irregular_rejected" or cadence is None:
        if cadence_decision.reason_code == "insufficient_observations":
            raise CadenceInferenceError(
                "observation cadence cannot be inferred with fewer than 3 points"
            )
        if cadence_decision.reason_code == "non_increasing_periods":
            raise CadenceInferenceError(
                "observation cadence cannot be inferred from non-increasing periods"
            )
        raise CadenceInferenceError(
            "observation cadence cannot be inferred from irregular spacing "
            f"({cadence_decision.reason_code})"
        )

    applicability_results = []
    snapshots = []
    for lookback in lookback_catalog:
        applicability, snapshot = _evaluate_lookback(
            observations,
            cadence=cadence,
            lookback_points=lookback,
        )
        applicability_results.append(applicability)
        if snapshot is not None:
            snapshots.append(snapshot)

    canonical = compute_canonical_descriptor(snapshots)
    return MultiLookbackEvaluationResult(
        analysis_version=build_result(
            outcome="insufficient_data",
            signature=None,
            start_period=None,
            end_period=None,
            reason="extracting_analysis_version",
        ).analysis_version,
        weighting_version=canonical.weighting_version,
        evaluated_observation_count=len(observations),
        cadence_decision=cadence_decision,
        applicability=tuple(applicability_results),
        lookback_snapshots=tuple(snapshots),
        canonical_descriptor=canonical,
    )
