"""Canonical arbitration for trend descriptor v2."""

from __future__ import annotations

from dataclasses import dataclass

from .models import (
    CanonicalTrendDescriptorResult,
    LookbackTrendSnapshotResult,
    build_canonical_descriptor,
)

TIEBREAK_CONFIDENCE_GAP_THRESHOLD = 0.05


@dataclass(frozen=True)
class ArbitrationWeights:
    short_horizon_weight: float = 0.25
    medium_horizon_weight: float = 0.60
    long_horizon_weight: float = 0.15


def _horizon_bucket(lookback_points: int) -> str:
    if lookback_points <= 10:
        return "short"
    if lookback_points <= 100:
        return "medium"
    return "long"


def _weight_for(snapshot: LookbackTrendSnapshotResult, weights: ArbitrationWeights) -> float:
    bucket = _horizon_bucket(snapshot.lookback_points)
    if bucket == "short":
        return weights.short_horizon_weight
    if bucket == "medium":
        return weights.medium_horizon_weight
    return weights.long_horizon_weight


def compute_canonical_descriptor_v2(
    snapshots: list[LookbackTrendSnapshotResult],
    *,
    weights: ArbitrationWeights = ArbitrationWeights(),
) -> CanonicalTrendDescriptorResult:
    """Select canonical descriptor from applicable lookback snapshots."""

    available = [
        snapshot
        for snapshot in snapshots
        if snapshot.descriptor_state == "available"
        and snapshot.outcome_state == "significant_trend"
        and snapshot.direction in {"up", "down", "flat"}
    ]
    if not available:
        return build_canonical_descriptor(
            descriptor_state="unavailable",
            trend_label=None,
            direction=None,
            confidence_score=None,
            dominant_measure_family="none",
            medium_horizon_weight=None,
            short_horizon_weight=None,
            long_horizon_weight=None,
            preprocessing=None,
            ols_diagnostics=None,
            strength=None,
            selected_lookback_points=None,
            reason_code="no_significant_trend",
            weighting_trace={"selected": None, "candidates": {}},
        )

    scored = sorted(
        (
            (
                snapshot.confidence_score * _weight_for(snapshot, weights),
                snapshot,
            )
            for snapshot in available
            if snapshot.confidence_score is not None
        ),
        key=lambda item: (-item[0], item[1].lookback_points),
    )
    if not scored:
        return build_canonical_descriptor(
            descriptor_state="unavailable",
            trend_label=None,
            direction=None,
            confidence_score=None,
            dominant_measure_family="none",
            medium_horizon_weight=None,
            short_horizon_weight=None,
            long_horizon_weight=None,
            preprocessing=None,
            ols_diagnostics=None,
            strength=None,
            selected_lookback_points=None,
            reason_code="no_scored_candidates",
            weighting_trace={"selected": None, "candidates": {}},
        )

    selected_score, selected = scored[0]
    if len(scored) > 1 and abs(selected_score - scored[1][0]) <= TIEBREAK_CONFIDENCE_GAP_THRESHOLD:
        best = sorted(
            [
                item
                for item in scored
                if abs(item[0] - selected_score) <= TIEBREAK_CONFIDENCE_GAP_THRESHOLD
            ],
            key=lambda item: (item[1].lookback_points, -item[0]),
        )
        selected_score, selected = best[0]

    return build_canonical_descriptor(
        descriptor_state="available",
        trend_label=selected.trend_label,
        direction=selected.direction,
        confidence_score=selected.confidence_score,
        dominant_measure_family=selected.dominant_measure_family,
        medium_horizon_weight=weights.medium_horizon_weight,
        short_horizon_weight=weights.short_horizon_weight,
        long_horizon_weight=weights.long_horizon_weight,
        preprocessing=selected.preprocessing,
        ols_diagnostics=selected.ols_diagnostics,
        strength=selected.strength,
        selected_lookback_points=selected.lookback_points,
        reason_code=None,
        weighting_trace={
            "selected": selected.lookback_points,
            "candidates": {str(item[1].lookback_points): item[0] for item in scored},
        },
    )
