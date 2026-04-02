"""Trend signature comparison helpers for lifecycle decisions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrendSignature:
    """Comparable signature dimensions for one classified trend state."""

    trend_label: str
    direction: str
    strength: str
    seasonality_classification: str


def signatures_match(*, left: TrendSignature, right: TrendSignature) -> bool:
    """Return whether two signatures represent the same lifecycle state."""
    return (
        left.trend_label == right.trend_label
        and left.direction == right.direction
        and left.strength == right.strength
        and left.seasonality_classification == right.seasonality_classification
    )
