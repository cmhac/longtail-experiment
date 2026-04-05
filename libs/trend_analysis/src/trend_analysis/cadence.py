"""Cadence inference helpers for deterministic trend analysis."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import Literal

from .models import CadenceDecisionResult, build_cadence_decision_result

Cadence = Literal["daily", "weekly", "monthly"]
MIN_OBSERVATIONS_FOR_CADENCE = 3
SUPPORTED_CADENCE_FAMILIES: tuple[Cadence, ...] = ("daily", "weekly", "monthly")
DOMINANT_CADENCE_REQUIRED = True
MAX_IRREGULAR_GAP_RATIO = 0.002
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


def _cadence_count_payload(
    *,
    daily_count: int,
    weekly_count: int,
    monthly_count: int,
    irregular_count: int,
) -> str:
    return (
        "daily="
        f"{daily_count},weekly={weekly_count},monthly={monthly_count},irregular={irregular_count}"
    )


def infer_cadence_decision(observations: Sequence[tuple[date, float]]) -> CadenceDecisionResult:
    """Infer cadence decision metadata for ordered observation spacing."""
    if len(observations) < MIN_OBSERVATIONS_FOR_CADENCE:
        return build_cadence_decision_result(
            cadence_state="irregular_rejected",
            inferred_cadence=None,
            irregular_gap_count=0,
            total_interval_count=max(len(observations) - 1, 0),
            irregular_gap_ratio=0.0,
            reason_code="insufficient_observations",
            reason_detail=("observation cadence cannot be inferred with fewer than 3 points"),
        )

    daily_count = 0
    weekly_count = 0
    monthly_count = 0
    irregular_count = 0
    for index in range(1, len(observations)):
        current = observations[index][0]
        previous = observations[index - 1][0]
        gap_days = (current - previous).days
        if gap_days <= 0:
            return build_cadence_decision_result(
                cadence_state="irregular_rejected",
                inferred_cadence=None,
                irregular_gap_count=irregular_count,
                total_interval_count=max(len(observations) - 1, 0),
                irregular_gap_ratio=0.0,
                reason_code="non_increasing_periods",
                reason_detail="observation cadence cannot be inferred from non-increasing periods",
            )

        classified = _classify_gap(gap_days)
        if classified == "daily":
            daily_count += 1
        elif classified == "weekly":
            weekly_count += 1
        elif classified == "monthly":
            monthly_count += 1
        else:
            irregular_count += 1

    total_interval_count = len(observations) - 1
    irregular_gap_ratio = irregular_count / total_interval_count

    cadence_counts: dict[Cadence, int] = {
        "daily": daily_count,
        "weekly": weekly_count,
        "monthly": monthly_count,
    }
    dominant_candidates: list[Cadence] = [
        cadence for cadence in SUPPORTED_CADENCE_FAMILIES if cadence_counts[cadence] > 0
    ]

    if not dominant_candidates:
        return build_cadence_decision_result(
            cadence_state="irregular_rejected",
            inferred_cadence=None,
            irregular_gap_count=irregular_count,
            total_interval_count=total_interval_count,
            irregular_gap_ratio=irregular_gap_ratio,
            reason_code="no_supported_cadence_gaps",
            reason_detail=_cadence_count_payload(
                daily_count=daily_count,
                weekly_count=weekly_count,
                monthly_count=monthly_count,
                irregular_count=irregular_count,
            ),
        )

    if DOMINANT_CADENCE_REQUIRED and len(dominant_candidates) != 1:
        return build_cadence_decision_result(
            cadence_state="irregular_rejected",
            inferred_cadence=None,
            irregular_gap_count=irregular_count,
            total_interval_count=total_interval_count,
            irregular_gap_ratio=irregular_gap_ratio,
            reason_code="mixed_cadence_families",
            reason_detail=_cadence_count_payload(
                daily_count=daily_count,
                weekly_count=weekly_count,
                monthly_count=monthly_count,
                irregular_count=irregular_count,
            ),
        )

    inferred_cadence = dominant_candidates[0]
    cadence_state: str
    inferred: Cadence | None
    reason_code: str
    reason_detail: str | None
    if irregular_count == 0:
        cadence_state = "regular"
        inferred = inferred_cadence
        reason_code = "regular_spacing"
        reason_detail = None
    elif irregular_gap_ratio <= MAX_IRREGULAR_GAP_RATIO:
        cadence_state = "gap_tolerant"
        inferred = inferred_cadence
        reason_code = "isolated_irregular_gaps_tolerated"
        reason_detail = f"ratio={irregular_gap_ratio:.6f},threshold={MAX_IRREGULAR_GAP_RATIO:.6f}"
    else:
        cadence_state = "irregular_rejected"
        inferred = None
        reason_code = "irregular_gap_ratio_exceeds_threshold"
        reason_detail = f"ratio={irregular_gap_ratio:.6f},threshold={MAX_IRREGULAR_GAP_RATIO:.6f}"

    return build_cadence_decision_result(
        cadence_state=cadence_state,
        inferred_cadence=inferred,
        irregular_gap_count=irregular_count,
        total_interval_count=total_interval_count,
        irregular_gap_ratio=irregular_gap_ratio,
        reason_code=reason_code,
        reason_detail=reason_detail,
    )


def infer_cadence(observations: Sequence[tuple[date, float]]) -> Cadence:
    """Infer cadence from ordered observation spacing or raise explicit failure."""
    decision = infer_cadence_decision(observations)
    if decision.reason_code == "insufficient_observations":
        raise CadenceInferenceError(
            "observation cadence cannot be inferred with fewer than 3 points"
        )
    if decision.reason_code == "non_increasing_periods":
        raise CadenceInferenceError(
            "observation cadence cannot be inferred from non-increasing periods"
        )
    if decision.cadence_state == "irregular_rejected" or decision.inferred_cadence is None:
        raise CadenceInferenceError(
            "observation cadence cannot be inferred from irregular spacing "
            f"({decision.reason_code})"
        )
    return decision.inferred_cadence
