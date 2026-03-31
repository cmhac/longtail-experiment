"""Trend lifecycle transition decisions for pipeline persistence flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, cast


class TrendAnalysisResultLike(Protocol):
    """Structural contract consumed from trend-analysis library outputs."""

    outcome: Literal["significant_trend", "no_significant_trend", "insufficient_data"]
    analysis_version: str
    signature: object | None


@dataclass(frozen=True)
class PersistedTrendSignature:
    """Persisted signature values used for continuity and replacement checks."""

    trend_label: str
    direction: str
    strength: str
    seasonality_classification: str
    analysis_version: str


@dataclass(frozen=True)
class TrendTransitionDecision:
    """One deterministic transition decision for trend lifecycle state."""

    transition_type: Literal["created", "continued", "replaced", "ended", "no_op"]
    reason: str
    analysis_version: str


class SeasonalityClassificationChangedError(RuntimeError):
    """Raised when seasonality classification changes in a continuing context."""


def _signature_changed(
    *,
    existing: PersistedTrendSignature,
    incoming: object,
) -> bool:
    incoming_trend_label = _signature_value(incoming, "trend_label")
    incoming_direction = _signature_value(incoming, "direction")
    incoming_strength = _signature_value(incoming, "strength")
    incoming_seasonality = _signature_value(incoming, "seasonality_classification")

    return (
        existing.trend_label != incoming_trend_label
        or existing.direction != incoming_direction
        or existing.strength != incoming_strength
        or existing.seasonality_classification != incoming_seasonality
    )


def _signature_value(signature: object, key: str) -> str:
    if isinstance(signature, dict):
        mapping = cast(dict[str, object], signature)
        value = mapping.get(key)
    else:
        value = getattr(signature, key, None)

    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"significant_trend signature missing required field: {key}")
    return value


def classify_trend_transition(
    *,
    existing: PersistedTrendSignature | None,
    analysis_result: TrendAnalysisResultLike,
) -> TrendTransitionDecision:
    """Classify one lifecycle transition from persisted and newly analyzed state."""
    if analysis_result.outcome == "insufficient_data":
        return TrendTransitionDecision(
            transition_type="no_op",
            reason="insufficient_data",
            analysis_version=analysis_result.analysis_version,
        )

    if analysis_result.outcome == "no_significant_trend":
        transition_type: Literal["no_op", "ended"] = "no_op"
        if existing is not None:
            transition_type = "ended"
        return TrendTransitionDecision(
            transition_type=transition_type,
            reason="no_significant_trend",
            analysis_version=analysis_result.analysis_version,
        )

    if analysis_result.signature is None:
        raise ValueError("significant_trend outcome requires a non-null signature")

    if existing is None:
        return TrendTransitionDecision(
            transition_type="created",
            reason="first_significant_trend",
            analysis_version=analysis_result.analysis_version,
        )

    if existing.analysis_version != analysis_result.analysis_version:
        return TrendTransitionDecision(
            transition_type="replaced",
            reason="analysis_version_changed",
            analysis_version=analysis_result.analysis_version,
        )

    if existing.seasonality_classification != _signature_value(
        analysis_result.signature, "seasonality_classification"
    ):
        raise SeasonalityClassificationChangedError(
            "seasonality classification changed for continuing trend context"
        )

    if _signature_changed(existing=existing, incoming=analysis_result.signature):
        return TrendTransitionDecision(
            transition_type="replaced",
            reason="trend_signature_changed",
            analysis_version=analysis_result.analysis_version,
        )

    return TrendTransitionDecision(
        transition_type="continued",
        reason="trend_signature_unchanged",
        analysis_version=analysis_result.analysis_version,
    )
