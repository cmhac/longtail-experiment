"""Typed trend analysis result models shared across library consumers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

from .version import CANONICAL_WEIGHTING_VERSION, LIBRARY_VERSION

TrendOutcome = Literal[
    "significant_trend",
    "no_significant_trend",
    "insufficient_data",
]
CadenceFamily = Literal["daily", "weekly", "monthly"]
CadenceState = Literal["regular", "gap_tolerant", "irregular_rejected"]
LookbackApplicabilityState = Literal["applicable", "inapplicable"]
LookbackOutcomeState = Literal["significant_trend", "no_significant_trend"]
CanonicalDescriptorState = Literal["available", "unavailable"]


@dataclass(frozen=True)
class PreprocessingMetadata:
    """Preprocessing metadata for one evaluated lookback."""

    smoothing_method: Literal["ewma", "none"]
    smoothing_parameters: dict[str, object]
    seasonal_adjustment_method: Literal["stl", "mstl", "none"]
    seasonal_periods: tuple[int, ...]
    seasonal_reliability_state: Literal["reliable", "fallback_non_adjusted", "not_applicable"]
    preprocess_version: str


@dataclass(frozen=True)
class OlsDiagnostics:
    """Supplementary linear diagnostics for one lookback."""

    slope: float | None
    intercept: float | None
    r_squared: float | None
    p_value: float | None


@dataclass(frozen=True)
class TrendSignature:
    """Persisted signature dimensions used for lifecycle continuity checks."""

    trend_label: str
    direction: Literal["up", "down"]
    strength: Literal["mild", "strong"]
    seasonality_classification: Literal["seasonal", "non_seasonal"]


@dataclass(frozen=True)
class TrendAnalysisResult:
    """Pure deterministic output returned by the trend-analysis library."""

    outcome: TrendOutcome
    analysis_version: str
    signature: TrendSignature | None
    start_period: date | None
    end_period: date | None
    reason: str


@dataclass(frozen=True)
class LookbackApplicabilityResult:
    """Applicability decision for one lookback depth."""

    lookback_points: int
    applicability_state: LookbackApplicabilityState
    reason_code: str
    reason_detail: str | None


@dataclass(frozen=True)
class LookbackTrendSnapshotResult:
    """Per-lookback trend classification result for one observation."""

    lookback_points: int
    outcome_state: LookbackOutcomeState
    analysis_version: str
    trend_label: str | None
    descriptor_state: Literal["available", "unavailable"]
    direction: Literal["up", "down", "flat"] | None
    confidence_score: float | None
    dominant_measure_family: Literal["theil_sen", "mixed", "none"]
    theil_sen_slope: float | None
    theil_sen_low_slope: float | None
    theil_sen_high_slope: float | None
    kendall_tau: float | None
    kendall_pvalue: float | None
    preprocessing: PreprocessingMetadata
    ols_diagnostics: OlsDiagnostics
    strength: Literal["mild", "strong"] | None
    seasonality_classification: Literal["seasonal", "non_seasonal"] | None
    reason_code: str | None
    reason: str


@dataclass(frozen=True)
class CanonicalTrendDescriptorResult:
    """Weighted canonical descriptor derived from applicable lookback snapshots."""

    descriptor_version: Literal["v2"]
    descriptor_state: CanonicalDescriptorState
    weighting_version: str
    trend_label: str | None
    direction: Literal["up", "down", "flat"] | None
    confidence_score: float | None
    dominant_measure_family: Literal["theil_sen", "mixed", "none"]
    medium_horizon_weight: float | None
    short_horizon_weight: float | None
    long_horizon_weight: float | None
    preprocessing: PreprocessingMetadata | None
    ols_diagnostics: OlsDiagnostics | None
    strength: Literal["mild", "strong"] | None
    selected_lookback_points: int | None
    reason_code: str | None
    weighting_trace: dict[str, object] | None


@dataclass(frozen=True)
class CadenceDecisionResult:
    """Deterministic cadence decision output for one ordered observation history."""

    cadence_state: CadenceState
    inferred_cadence: CadenceFamily | None
    irregular_gap_count: int
    total_interval_count: int
    irregular_gap_ratio: float
    reason_code: str
    reason_detail: str | None


@dataclass(frozen=True)
class MultiLookbackEvaluationResult:
    """Full multi-lookback evaluation payload for one observation context."""

    analysis_version: str
    weighting_version: str
    evaluated_observation_count: int
    cadence_decision: CadenceDecisionResult
    applicability: tuple[LookbackApplicabilityResult, ...]
    lookback_snapshots: tuple[LookbackTrendSnapshotResult, ...]
    canonical_descriptor: CanonicalTrendDescriptorResult


def build_cadence_decision_result(
    *,
    cadence_state: CadenceState,
    inferred_cadence: CadenceFamily | None,
    irregular_gap_count: int,
    total_interval_count: int,
    irregular_gap_ratio: float,
    reason_code: str,
    reason_detail: str | None,
) -> CadenceDecisionResult:
    """Build a typed cadence decision result."""
    return CadenceDecisionResult(
        cadence_state=cadence_state,
        inferred_cadence=inferred_cadence,
        irregular_gap_count=irregular_gap_count,
        total_interval_count=total_interval_count,
        irregular_gap_ratio=irregular_gap_ratio,
        reason_code=reason_code,
        reason_detail=reason_detail,
    )


def build_result(
    *,
    outcome: TrendOutcome,
    signature: TrendSignature | None,
    start_period: date | None,
    end_period: date | None,
    reason: str,
) -> TrendAnalysisResult:
    """Build one typed result with version identity bound to library version."""
    return TrendAnalysisResult(
        outcome=outcome,
        analysis_version=LIBRARY_VERSION,
        signature=signature,
        start_period=start_period,
        end_period=end_period,
        reason=reason,
    )


def build_lookback_applicability_result(
    *,
    lookback_points: int,
    applicability_state: LookbackApplicabilityState,
    reason_code: str,
    reason_detail: str | None,
) -> LookbackApplicabilityResult:
    """Build a typed lookback applicability decision."""
    return LookbackApplicabilityResult(
        lookback_points=lookback_points,
        applicability_state=applicability_state,
        reason_code=reason_code,
        reason_detail=reason_detail,
    )


def build_lookback_snapshot_result(
    *,
    lookback_points: int,
    outcome_state: LookbackOutcomeState,
    trend_label: str | None,
    descriptor_state: Literal["available", "unavailable"] = "available",
    direction: Literal["up", "down", "flat"] | None,
    confidence_score: float | None = None,
    dominant_measure_family: Literal["theil_sen", "mixed", "none"] = "none",
    theil_sen_slope: float | None = None,
    theil_sen_low_slope: float | None = None,
    theil_sen_high_slope: float | None = None,
    kendall_tau: float | None = None,
    kendall_pvalue: float | None = None,
    preprocessing: PreprocessingMetadata | None = None,
    ols_diagnostics: OlsDiagnostics | None = None,
    strength: Literal["mild", "strong"] | None,
    seasonality_classification: Literal["seasonal", "non_seasonal"] | None,
    reason_code: str | None = None,
    reason: str,
) -> LookbackTrendSnapshotResult:
    """Build one typed lookback snapshot result."""
    resolved_preprocessing = preprocessing or PreprocessingMetadata(
        smoothing_method="none",
        smoothing_parameters={},
        seasonal_adjustment_method="none",
        seasonal_periods=(),
        seasonal_reliability_state="not_applicable",
        preprocess_version=LIBRARY_VERSION,
    )
    resolved_ols = ols_diagnostics or OlsDiagnostics(
        slope=None,
        intercept=None,
        r_squared=None,
        p_value=None,
    )
    return LookbackTrendSnapshotResult(
        lookback_points=lookback_points,
        outcome_state=outcome_state,
        analysis_version=LIBRARY_VERSION,
        trend_label=trend_label,
        descriptor_state=descriptor_state,
        direction=direction,
        confidence_score=confidence_score,
        dominant_measure_family=dominant_measure_family,
        theil_sen_slope=theil_sen_slope,
        theil_sen_low_slope=theil_sen_low_slope,
        theil_sen_high_slope=theil_sen_high_slope,
        kendall_tau=kendall_tau,
        kendall_pvalue=kendall_pvalue,
        preprocessing=resolved_preprocessing,
        ols_diagnostics=resolved_ols,
        strength=strength,
        seasonality_classification=seasonality_classification,
        reason_code=reason_code,
        reason=reason,
    )


def build_canonical_descriptor(
    *,
    descriptor_version: Literal["v2"] = "v2",
    descriptor_state: CanonicalDescriptorState,
    trend_label: str | None,
    direction: Literal["up", "down", "flat"] | None,
    confidence_score: float | None = None,
    dominant_measure_family: Literal["theil_sen", "mixed", "none"] = "none",
    medium_horizon_weight: float | None = None,
    short_horizon_weight: float | None = None,
    long_horizon_weight: float | None = None,
    preprocessing: PreprocessingMetadata | None = None,
    ols_diagnostics: OlsDiagnostics | None = None,
    strength: Literal["mild", "strong"] | None,
    selected_lookback_points: int | None,
    reason_code: str | None,
    weighting_trace: dict[str, object] | None,
) -> CanonicalTrendDescriptorResult:
    """Build canonical descriptor with version metadata."""
    return CanonicalTrendDescriptorResult(
        descriptor_version=descriptor_version,
        descriptor_state=descriptor_state,
        weighting_version=CANONICAL_WEIGHTING_VERSION,
        trend_label=trend_label,
        direction=direction,
        confidence_score=confidence_score,
        dominant_measure_family=dominant_measure_family,
        medium_horizon_weight=medium_horizon_weight,
        short_horizon_weight=short_horizon_weight,
        long_horizon_weight=long_horizon_weight,
        preprocessing=preprocessing,
        ols_diagnostics=ols_diagnostics,
        strength=strength,
        selected_lookback_points=selected_lookback_points,
        reason_code=reason_code,
        weighting_trace=weighting_trace,
    )
