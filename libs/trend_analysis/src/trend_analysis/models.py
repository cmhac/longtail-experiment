"""Typed trend analysis result models shared across library consumers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

from .version import LIBRARY_VERSION

TrendOutcome = Literal[
    "significant_trend",
    "no_significant_trend",
    "insufficient_data",
]


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
