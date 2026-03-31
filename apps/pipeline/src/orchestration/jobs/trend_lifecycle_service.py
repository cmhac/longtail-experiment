"""Service for applying trend-analysis outcomes to lifecycle persistence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, cast

from ..resources.trend_repository import TrendRepository
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

            self._repository.upsert_trend_record(
                {
                    "series_key": series_key,
                    "trend_label": existing_trend.trend_label,
                    "direction": existing_trend.direction,
                    "strength": existing_trend.strength,
                    "seasonality_classification": existing_trend.seasonality_classification,
                    "start_period": latest_observation_on,
                    "end_period": latest_observation_on,
                    "is_ongoing": False,
                }
            )
            self._repository.append_transition(
                {
                    "series_key": series_key,
                    "transition_type": "ended",
                    "prior_trend_record_id": existing_trend.trend_record_id,
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
                "prior_trend_record_id": (
                    existing_trend.trend_record_id if existing_trend is not None else None
                ),
                "new_trend_record_id": new_record_id,
                "trigger_observation_on": latest_observation_on,
                "reason": decision.reason,
            }
        )
        return TrendLifecycleApplyResult(
            outcome_state="applied",
            outcome_reason_code=decision.transition_type,
        )
