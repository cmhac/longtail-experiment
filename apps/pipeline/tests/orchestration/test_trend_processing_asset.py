"""US1 tests for per-series downstream trend-processing helpers."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_lifecycle_service import (
    PersistedTrendSnapshot,
    TrendLifecycleApplyResult,
)
from src.orchestration.jobs.trend_processing_asset import process_updated_series
from src.orchestration.jobs.trend_transition_logic import TrendAnalysisResultLike


@dataclass(frozen=True)
class FakeAnalysisResult:
    """Minimal trend-analysis shape consumed by downstream helpers."""

    outcome: Literal["significant_trend", "no_significant_trend", "insufficient_data"]
    analysis_version: str
    signature: dict[str, str] | None


class FakeLifecycleApplier:
    """Capture invocation order and return stable no-op metadata."""

    def __init__(self) -> None:
        """Initialize call-tracking state for per-series execution assertions."""
        self.calls: list[str] = []

    def apply_analysis_result(
        self,
        *,
        series_key: str,
        latest_observation_on: datetime,
        analysis_result,
        existing_trend: PersistedTrendSnapshot | None,
    ) -> TrendLifecycleApplyResult:
        """Record one call and return deterministic no-op metadata."""
        self.calls.append(series_key)
        return TrendLifecycleApplyResult(
            outcome_state="no_op",
            outcome_reason_code="no_significant_trend",
        )


def test_process_updated_series_emits_per_series_metadata_in_order() -> None:
    """Downstream trend stage should execute per updated series deterministically."""
    applier = FakeLifecycleApplier()
    updated_series: list[
        tuple[
            str,
            datetime,
            TrendAnalysisResultLike,
            PersistedTrendSnapshot | None,
        ]
    ] = [
        (
            "SERIES.A",
            datetime(2026, 3, 1, tzinfo=UTC),
            cast(
                TrendAnalysisResultLike,
                FakeAnalysisResult(
                    outcome="no_significant_trend",
                    analysis_version="0.1.0",
                    signature=None,
                ),
            ),
            None,
        ),
        (
            "SERIES.B",
            datetime(2026, 3, 1, tzinfo=UTC),
            cast(
                TrendAnalysisResultLike,
                FakeAnalysisResult(
                    outcome="insufficient_data",
                    analysis_version="0.1.0",
                    signature=None,
                ),
            ),
            None,
        ),
    ]
    metadata = process_updated_series(
        updated_series=updated_series,
        lifecycle_applier=applier,
    )

    assert applier.calls == ["SERIES.A", "SERIES.B"]
    assert [item.series_key for item in metadata] == ["SERIES.A", "SERIES.B"]
    assert all(item.execution_state == "no_op" for item in metadata)
    assert all(item.outcome_reason_code == "no_significant_trend" for item in metadata)
