"""Service for applying trend-analysis outcomes to lifecycle persistence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal, Protocol, cast

from ..resources.trend_repository import (
    CanonicalDescriptorInsert,
    LookbackSnapshotInsert,
    TrendRepository,
)
from .trend_transition_logic import (
    PersistedTrendSignature,
    TrendAnalysisResultLike,
    classify_trend_transition,
)


@dataclass(frozen=True)
class PersistedTrendSnapshot:
    """Current persisted ongoing-trend snapshot for one series."""

    trend_record_id: str
    trend_label: str
    direction: str
    strength: str
    seasonality_classification: str
    analysis_version: str


@dataclass(frozen=True)
class TrendLifecycleApplyResult:
    """Outcome metadata emitted after one lifecycle apply attempt."""

    outcome_state: Literal["applied", "no_op"]
    outcome_reason_code: str


@dataclass(frozen=True)
class TrendLookbackApplyResult:
    """Outcome emitted after applying one lookback evaluation payload."""

    outcome_state: Literal["applied", "partial_applied"]
    outcome_reason_code: str
    cadence_decision: dict[str, object] | None = None


class LookbackEvaluationResultLike(Protocol):
    """Structural shape required for lookback persistence apply flow."""

    applicability: tuple[LookbackApplicabilityLike, ...]
    lookback_snapshots: tuple[LookbackSnapshotLike, ...]
    canonical_descriptor: CanonicalDescriptorLike
    cadence_decision: CadenceDecisionLike


class CadenceDecisionLike(Protocol):
    """Structural cadence decision metadata item."""

    cadence_state: Literal["regular", "gap_tolerant", "irregular_rejected"]
    inferred_cadence: Literal["daily", "weekly", "monthly"] | None
    irregular_gap_count: int
    total_interval_count: int
    irregular_gap_ratio: float
    reason_code: str
    reason_detail: str | None


class LookbackApplicabilityLike(Protocol):
    """Structural lookback applicability item."""

    lookback_points: int
    applicability_state: Literal["applicable", "inapplicable"]
    reason_code: str
    reason_detail: str | None


class LookbackSnapshotLike(Protocol):
    """Structural lookback snapshot item."""

    lookback_points: int
    outcome_state: Literal["significant_trend", "no_significant_trend"]
    descriptor_state: Literal["available", "unavailable"]
    trend_label: str | None
    direction: Literal["up", "down", "flat"] | None
    confidence_score: float | None
    dominant_measure_family: Literal["theil_sen", "mixed", "none"]
    theil_sen_slope: float | None
    theil_sen_low_slope: float | None
    theil_sen_high_slope: float | None
    kendall_tau: float | None
    kendall_pvalue: float | None
    preprocessing: object
    ols_diagnostics: object
    strength: str | None
    seasonality_classification: str | None
    reason_code: str | None
    analysis_version: str


class CanonicalDescriptorLike(Protocol):
    """Structural canonical descriptor item."""

    descriptor_version: Literal["v2"]
    descriptor_state: Literal["available", "unavailable"]
    trend_label: str | None
    direction: Literal["up", "down", "flat"] | None
    confidence_score: float | None
    dominant_measure_family: Literal["theil_sen", "mixed", "none"]
    medium_horizon_weight: float | None
    short_horizon_weight: float | None
    long_horizon_weight: float | None
    preprocessing: object
    ols_diagnostics: object
    strength: str | None
    selected_lookback_points: int | None
    reason_code: str | None
    weighting_version: str
    weighting_trace: dict[str, object] | None


def _signature_value(signature: object, key: str) -> str:
    mapping = cast(dict[str, object], signature) if isinstance(signature, dict) else None
    value = mapping.get(key) if mapping is not None else getattr(signature, key, None)

    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"significant_trend signature missing required field: {key}")
    return value


class TrendLifecycleService:
    """Apply one analysis result into trend record + transition persistence writes."""

    def __init__(self, *, repository: TrendRepository) -> None:
        """Initialize service with trend lifecycle persistence dependency."""
        self._repository = repository

    @staticmethod
    def classify_notification_visibility(
        *,
        run_full_backfill: bool,
    ) -> tuple[
        Literal["incremental", "historical_reprocessing"],
        Literal["user_visible", "audit_only"],
    ]:
        """Resolve processing context and notification visibility classification."""
        if run_full_backfill:
            return ("historical_reprocessing", "audit_only")
        return ("incremental", "user_visible")

    @staticmethod
    def resolve_notification_direction(
        *,
        descriptor_state: str,
        direction: str | None,
    ) -> Literal["up", "down"] | None:
        """Return directional-only notification signal from canonical descriptor fields."""

        if descriptor_state != "available":
            return None
        if direction not in {"up", "down"}:
            return None
        return cast(Literal["up", "down"], direction)

    def apply_analysis_result(
        self,
        *,
        series_key: str,
        latest_observation_on: datetime,
        analysis_result: TrendAnalysisResultLike,
        existing_trend: PersistedTrendSnapshot | None,
    ) -> TrendLifecycleApplyResult:
        """Apply trend lifecycle mutation decisions with state-based idempotency."""
        existing_signature = (
            PersistedTrendSignature(
                trend_label=existing_trend.trend_label,
                direction=existing_trend.direction,
                strength=existing_trend.strength,
                seasonality_classification=existing_trend.seasonality_classification,
                analysis_version=existing_trend.analysis_version,
            )
            if existing_trend is not None
            else None
        )

        decision = classify_trend_transition(
            existing=existing_signature,
            analysis_result=analysis_result,
        )

        if decision.transition_type in {"no_op", "continued"}:
            return TrendLifecycleApplyResult(
                outcome_state="no_op",
                outcome_reason_code=decision.reason,
            )

        if decision.transition_type == "ended":
            if existing_trend is None:
                return TrendLifecycleApplyResult(
                    outcome_state="no_op",
                    outcome_reason_code="no_existing_trend",
                )

            closed_record_id = self._repository.close_ongoing_trend_for_series(
                series_key=series_key,
                end_period=latest_observation_on,
            )
            prior_id = closed_record_id or existing_trend.trend_record_id
            self._repository.append_transition(
                {
                    "series_key": series_key,
                    "transition_type": "ended",
                    "prior_trend_record_id": prior_id,
                    "new_trend_record_id": None,
                    "trigger_observation_on": latest_observation_on,
                    "reason": decision.reason,
                }
            )
            return TrendLifecycleApplyResult(
                outcome_state="applied",
                outcome_reason_code="trend_ended",
            )

        signature = analysis_result.signature
        if signature is None:
            raise ValueError("significant_trend outcome requires signature for lifecycle writes")

        prior_record_id = existing_trend.trend_record_id if existing_trend is not None else None
        if existing_trend is not None and decision.transition_type == "replaced":
            closed_record_id = self._repository.close_ongoing_trend_for_series(
                series_key=series_key,
                end_period=latest_observation_on,
            )
            if closed_record_id is not None:
                prior_record_id = closed_record_id

        new_record_id = self._repository.upsert_trend_record(
            {
                "series_key": series_key,
                "trend_label": _signature_value(signature, "trend_label"),
                "direction": _signature_value(signature, "direction"),
                "strength": _signature_value(signature, "strength"),
                "seasonality_classification": _signature_value(
                    signature,
                    "seasonality_classification",
                ),
                "start_period": latest_observation_on,
                "end_period": None,
                "is_ongoing": True,
            }
        )
        self._repository.append_transition(
            {
                "series_key": series_key,
                "transition_type": decision.transition_type,
                "prior_trend_record_id": prior_record_id,
                "new_trend_record_id": new_record_id,
                "trigger_observation_on": latest_observation_on,
                "reason": decision.reason,
            }
        )
        return TrendLifecycleApplyResult(
            outcome_state="applied",
            outcome_reason_code=decision.transition_type,
        )

    def apply_lookback_evaluation(
        self,
        *,
        series_key: str,
        observed_on: date,
        observation_id: str | None,
        evaluation_result: object,
    ) -> TrendLookbackApplyResult:
        """Persist lookback applicability/snapshots and canonical descriptor payloads."""
        typed_result = cast(LookbackEvaluationResultLike, evaluation_result)
        applicability = typed_result.applicability
        snapshots = typed_result.lookback_snapshots
        canonical = typed_result.canonical_descriptor
        cadence_decision = typed_result.cadence_decision
        cadence_decision_payload: dict[str, object] = {
            "cadence_state": cadence_decision.cadence_state,
            "inferred_cadence": cadence_decision.inferred_cadence,
            "irregular_gap_count": cadence_decision.irregular_gap_count,
            "total_interval_count": cadence_decision.total_interval_count,
            "irregular_gap_ratio": cadence_decision.irregular_gap_ratio,
            "reason_code": cadence_decision.reason_code,
            "reason_detail": cadence_decision.reason_detail,
        }

        first_snapshot_error: Exception | None = None
        for item in applicability:
            self._repository.upsert_lookback_applicability(
                {
                    "series_key": series_key,
                    "observed_on": observed_on,
                    "observation_id": observation_id,
                    "lookback_points": item.lookback_points,
                    "applicability_state": item.applicability_state,
                    "reason_code": item.reason_code,
                    "reason_detail": item.reason_detail,
                }
            )

        for snapshot in snapshots:
            try:
                snapshot_preprocessing_payload: dict[str, object] | None
                if hasattr(snapshot.preprocessing, "__dict__"):
                    snapshot_preprocessing_payload = cast(
                        dict[str, object], snapshot.preprocessing.__dict__
                    )
                elif isinstance(snapshot.preprocessing, dict):
                    snapshot_preprocessing_payload = cast(dict[str, object], snapshot.preprocessing)
                else:
                    snapshot_preprocessing_payload = None

                snapshot_payload: LookbackSnapshotInsert = {
                    "series_key": series_key,
                    "observed_on": observed_on,
                    "observation_id": observation_id,
                    "lookback_points": snapshot.lookback_points,
                    "outcome_state": snapshot.outcome_state,
                    "descriptor_state": snapshot.descriptor_state,
                    "trend_label": snapshot.trend_label,
                    "direction": snapshot.direction,
                    "confidence_score": snapshot.confidence_score,
                    "dominant_measure_family": snapshot.dominant_measure_family,
                    "theil_sen_slope": snapshot.theil_sen_slope,
                    "theil_sen_low_slope": snapshot.theil_sen_low_slope,
                    "theil_sen_high_slope": snapshot.theil_sen_high_slope,
                    "kendall_tau": snapshot.kendall_tau,
                    "kendall_pvalue": snapshot.kendall_pvalue,
                    "preprocessing": snapshot_preprocessing_payload,
                    "ols_slope": getattr(snapshot.ols_diagnostics, "slope", None),
                    "ols_intercept": getattr(snapshot.ols_diagnostics, "intercept", None),
                    "ols_r_squared": getattr(snapshot.ols_diagnostics, "r_squared", None),
                    "ols_pvalue": getattr(snapshot.ols_diagnostics, "p_value", None),
                    "reason_code": snapshot.reason_code,
                    "strength": snapshot.strength,
                    "seasonality_classification": snapshot.seasonality_classification,
                    "analysis_version": snapshot.analysis_version,
                }
                self._repository.upsert_lookback_snapshot(snapshot_payload)
            except Exception as exc:  # pragma: no cover - failure isolation boundary
                # Intentionally isolate per-lookback write failures so remaining
                # lookbacks and canonical descriptor still persist for this series.
                if first_snapshot_error is None:
                    first_snapshot_error = exc

        canonical_preprocessing_payload: dict[str, object] | None
        if canonical.preprocessing is not None and hasattr(canonical.preprocessing, "__dict__"):
            canonical_preprocessing_payload = cast(
                dict[str, object], canonical.preprocessing.__dict__
            )
        elif isinstance(canonical.preprocessing, dict):
            canonical_preprocessing_payload = cast(dict[str, object], canonical.preprocessing)
        else:
            canonical_preprocessing_payload = None

        canonical_payload: CanonicalDescriptorInsert = {
            "series_key": series_key,
            "observed_on": observed_on,
            "observation_id": observation_id,
            "descriptor_version": canonical.descriptor_version,
            "descriptor_state": canonical.descriptor_state,
            "canonical_trend_label": canonical.trend_label,
            "canonical_direction": canonical.direction,
            "confidence_score": canonical.confidence_score,
            "dominant_measure_family": canonical.dominant_measure_family,
            "medium_horizon_weight": canonical.medium_horizon_weight,
            "short_horizon_weight": canonical.short_horizon_weight,
            "long_horizon_weight": canonical.long_horizon_weight,
            "preprocessing": canonical_preprocessing_payload,
            "ols_slope": (
                None
                if canonical.ols_diagnostics is None
                else getattr(canonical.ols_diagnostics, "slope", None)
            ),
            "ols_intercept": (
                None
                if canonical.ols_diagnostics is None
                else getattr(canonical.ols_diagnostics, "intercept", None)
            ),
            "ols_r_squared": (
                None
                if canonical.ols_diagnostics is None
                else getattr(canonical.ols_diagnostics, "r_squared", None)
            ),
            "ols_pvalue": (
                None
                if canonical.ols_diagnostics is None
                else getattr(canonical.ols_diagnostics, "p_value", None)
            ),
            "reason_code": canonical.reason_code,
            "canonical_strength": canonical.strength,
            "selected_lookback_points": canonical.selected_lookback_points,
            "weighting_version": canonical.weighting_version,
            "weighting_trace": canonical.weighting_trace,
        }
        self._repository.upsert_canonical_descriptor(canonical_payload)

        if first_snapshot_error is not None:
            return TrendLookbackApplyResult(
                outcome_state="partial_applied",
                outcome_reason_code="partial_lookback_write_failure",
                cadence_decision=cadence_decision_payload,
            )
        return TrendLookbackApplyResult(
            outcome_state="applied",
            outcome_reason_code="lookback_snapshots_persisted",
            cadence_decision=cadence_decision_payload,
        )
