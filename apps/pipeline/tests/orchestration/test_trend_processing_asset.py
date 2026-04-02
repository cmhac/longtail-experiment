"""US1 tests for per-series downstream trend-processing helpers."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_lifecycle_service import (
    TrendLookbackApplyResult,
)
from src.orchestration.jobs.trend_processing_asset import process_updated_series


@dataclass(frozen=True)
class FakeEvaluationResult:
    """Minimal lookback-evaluation shape consumed by downstream helpers."""

    applicability: tuple[object, ...]
    lookback_snapshots: tuple[object, ...]
    canonical_descriptor: object


class FakeLifecycleApplier:
    """Capture invocation order and return stable no-op metadata."""

    def __init__(self) -> None:
        """Initialize call-tracking state for per-series execution assertions."""
        self.calls: list[str] = []

    def apply_lookback_evaluation(
        self,
        *,
        series_key: str,
        observed_on: date,
        observation_id: str | None,
        evaluation_result: object,
    ) -> TrendLookbackApplyResult:
        """Record one call and return deterministic no-op metadata."""
        self.calls.append(series_key)
        return TrendLookbackApplyResult(
            outcome_state="applied",
            outcome_reason_code="lookback_snapshots_persisted",
        )


def test_process_updated_series_emits_per_series_metadata_in_order() -> None:
    """Downstream trend stage should execute per updated series deterministically."""
    applier = FakeLifecycleApplier()
    updated_series: list[
        tuple[
            str,
            date,
            str | None,
            object,
        ]
    ] = [
        (
            "SERIES.A",
            date(2026, 3, 1),
            None,
            cast(
                object,
                FakeEvaluationResult(
                    applicability=(),
                    lookback_snapshots=(),
                    canonical_descriptor=object(),
                ),
            ),
        ),
        (
            "SERIES.B",
            date(2026, 3, 1),
            None,
            cast(
                object,
                FakeEvaluationResult(
                    applicability=(),
                    lookback_snapshots=(),
                    canonical_descriptor=object(),
                ),
            ),
        ),
    ]
    metadata = process_updated_series(
        updated_series=updated_series,
        lookback_applier=applier,
    )

    assert applier.calls == ["SERIES.A", "SERIES.B"]
    assert [item.series_key for item in metadata] == ["SERIES.A", "SERIES.B"]
    assert all(item.execution_state == "applied" for item in metadata)
    assert all(item.outcome_reason_code == "lookback_snapshots_persisted" for item in metadata)
