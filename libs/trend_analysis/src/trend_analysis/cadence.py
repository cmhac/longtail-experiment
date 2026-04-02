"""Cadence inference helpers for deterministic trend analysis."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import Literal

Cadence = Literal["daily", "weekly", "monthly"]
MIN_OBSERVATIONS_FOR_CADENCE = 3
DAILY_GAP_MIN = 1
DAILY_GAP_MAX = 2
WEEKLY_GAP_MIN = 6
WEEKLY_GAP_MAX = 8
MONTHLY_GAP_MIN = 28
MONTHLY_GAP_MAX = 31


class CadenceInferenceError(ValueError):
    """Raised when observation cadence cannot be inferred confidently."""


def _classify_gap(gap_days: int) -> Cadence | None:
    if DAILY_GAP_MIN <= gap_days <= DAILY_GAP_MAX:
        return "daily"
    if WEEKLY_GAP_MIN <= gap_days <= WEEKLY_GAP_MAX:
        return "weekly"
    if MONTHLY_GAP_MIN <= gap_days <= MONTHLY_GAP_MAX:
        return "monthly"
    return None


def infer_cadence(observations: Sequence[tuple[date, float]]) -> Cadence:
    """Infer cadence from ordered observation spacing or raise explicit failure."""
    if len(observations) < MIN_OBSERVATIONS_FOR_CADENCE:
        raise CadenceInferenceError(
            "observation cadence cannot be inferred with fewer than 3 points"
        )

    gaps: list[int] = []
    for index in range(1, len(observations)):
        current = observations[index][0]
        previous = observations[index - 1][0]
        gap_days = (current - previous).days
        if gap_days <= 0:
            raise CadenceInferenceError(
                "observation cadence cannot be inferred from non-increasing periods"
            )
        gaps.append(gap_days)

    inferred = {_classify_gap(gap) for gap in gaps}
    if None in inferred or len(inferred) != 1:
        raise CadenceInferenceError("observation cadence cannot be inferred from irregular spacing")

    only_cadence = next(iter(inferred))
    if only_cadence is None:
        raise CadenceInferenceError("observation cadence cannot be inferred from irregular spacing")
    return only_cadence
