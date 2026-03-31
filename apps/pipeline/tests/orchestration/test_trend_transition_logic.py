"""US1 tests for trend lifecycle transition decisions."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_transition_logic import (
    PersistedTrendSignature,
    SeasonalityClassificationChangedError,
    TrendAnalysisResultLike,
    classify_trend_transition,
)

LIBRARY_VERSION = "0.1.0"


@dataclass(frozen=True)
class FakeAnalysisResult:
    """Minimal structural view of trend analysis output for transition tests."""

    outcome: Literal["significant_trend", "no_significant_trend", "insufficient_data"]
    analysis_version: str
    signature: dict[str, str] | None


def test_create_transition_for_first_significant_result() -> None:
    """A first significant result should create a new ongoing trend segment."""
    result = FakeAnalysisResult(
        outcome="significant_trend",
        analysis_version=LIBRARY_VERSION,
        signature={
            "trend_label": "mild_sustained_uptrend",
            "direction": "up",
            "strength": "mild",
            "seasonality_classification": "non_seasonal",
        },
    )

    decision = classify_trend_transition(
        existing=None,
        analysis_result=cast(TrendAnalysisResultLike, result),
    )

    assert decision.transition_type == "created"
    assert decision.analysis_version == LIBRARY_VERSION


def test_continue_transition_when_signature_and_version_match() -> None:
    """Matching signature and analysis version should continue existing trend."""
    existing = PersistedTrendSignature(
        trend_label="mild_sustained_uptrend",
        direction="up",
        strength="mild",
        seasonality_classification="non_seasonal",
        analysis_version=LIBRARY_VERSION,
    )
    result = FakeAnalysisResult(
        outcome="significant_trend",
        analysis_version=LIBRARY_VERSION,
        signature={
            "trend_label": "mild_sustained_uptrend",
            "direction": "up",
            "strength": "mild",
            "seasonality_classification": "non_seasonal",
        },
    )

    decision = classify_trend_transition(
        existing=existing,
        analysis_result=cast(TrendAnalysisResultLike, result),
    )

    assert decision.transition_type == "continued"


def test_replace_transition_when_signature_changes() -> None:
    """Material signature changes should end/replace the ongoing trend segment."""
    existing = PersistedTrendSignature(
        trend_label="mild_sustained_uptrend",
        direction="up",
        strength="mild",
        seasonality_classification="non_seasonal",
        analysis_version=LIBRARY_VERSION,
    )
    result = FakeAnalysisResult(
        outcome="significant_trend",
        analysis_version=LIBRARY_VERSION,
        signature={
            "trend_label": "mild_sustained_downtrend",
            "direction": "down",
            "strength": "mild",
            "seasonality_classification": "non_seasonal",
        },
    )

    decision = classify_trend_transition(
        existing=existing,
        analysis_result=cast(TrendAnalysisResultLike, result),
    )

    assert decision.transition_type == "replaced"


def test_end_transition_when_no_significant_trend_found() -> None:
    """No significant result should end an ongoing trend if one exists."""
    existing = PersistedTrendSignature(
        trend_label="mild_sustained_uptrend",
        direction="up",
        strength="mild",
        seasonality_classification="non_seasonal",
        analysis_version=LIBRARY_VERSION,
    )
    result = FakeAnalysisResult(
        outcome="no_significant_trend",
        analysis_version=LIBRARY_VERSION,
        signature=None,
    )

    decision = classify_trend_transition(
        existing=existing,
        analysis_result=cast(TrendAnalysisResultLike, result),
    )

    assert decision.transition_type == "ended"


def test_raise_when_seasonality_changes_for_existing_trend() -> None:
    """Seasonality shifts for same context should fail fast at dataset scope."""
    existing = PersistedTrendSignature(
        trend_label="mild_sustained_uptrend",
        direction="up",
        strength="mild",
        seasonality_classification="non_seasonal",
        analysis_version=LIBRARY_VERSION,
    )
    result = FakeAnalysisResult(
        outcome="significant_trend",
        analysis_version=LIBRARY_VERSION,
        signature={
            "trend_label": "mild_sustained_uptrend",
            "direction": "up",
            "strength": "mild",
            "seasonality_classification": "seasonal",
        },
    )

    with pytest.raises(SeasonalityClassificationChangedError):
        classify_trend_transition(
            existing=existing,
            analysis_result=cast(TrendAnalysisResultLike, result),
        )


def test_replace_transition_when_analysis_version_changes() -> None:
    """Library-version change should force a replacement transition decision."""
    existing = PersistedTrendSignature(
        trend_label="mild_sustained_uptrend",
        direction="up",
        strength="mild",
        seasonality_classification="non_seasonal",
        analysis_version="0.0.1",
    )
    result = FakeAnalysisResult(
        outcome="significant_trend",
        analysis_version=LIBRARY_VERSION,
        signature={
            "trend_label": "mild_sustained_uptrend",
            "direction": "up",
            "strength": "mild",
            "seasonality_classification": "non_seasonal",
        },
    )

    decision = classify_trend_transition(
        existing=existing,
        analysis_result=cast(TrendAnalysisResultLike, result),
    )

    assert decision.transition_type == "replaced"
    assert decision.reason == "analysis_version_changed"
