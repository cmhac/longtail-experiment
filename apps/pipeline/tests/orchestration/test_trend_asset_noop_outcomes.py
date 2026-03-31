"""US1 integration-like tests for trend no-op lifecycle outcomes."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_lifecycle_service import TrendLifecycleService
from src.orchestration.jobs.trend_transition_logic import TrendAnalysisResultLike
from src.orchestration.resources.trend_repository import TrendRepository


@dataclass(frozen=True)
class FakeAnalysisResult:
    """Minimal trend-analysis result shape used by lifecycle service tests."""

    outcome: Literal["significant_trend", "no_significant_trend", "insufficient_data"]
    analysis_version: str
    signature: dict[str, str] | None


class FakeTrendRepository(TrendRepository):
    """Collect repository writes for assertion-friendly lifecycle tests."""

    def __init__(self) -> None:
        """Initialize empty write-collection buffers for assertions."""
        self.record_writes: list[dict[str, object]] = []
        self.transition_writes: list[dict[str, object]] = []

    def upsert_trend_record(self, payload):
        """Collect one trend record write and return a stable fake id."""
        self.record_writes.append(dict(payload))
        return "trend-record-id"

    def append_transition(self, payload):
        """Collect one transition write for downstream assertions."""
        self.transition_writes.append(dict(payload))


def test_no_significant_without_existing_trend_writes_no_lifecycle_rows() -> None:
    """No-significant trend outcome should emit explicit no-op metadata only."""
    repository = FakeTrendRepository()
    service = TrendLifecycleService(repository=repository)

    result = service.apply_analysis_result(
        series_key="SERIES.X",
        latest_observation_on=datetime(2026, 3, 1, tzinfo=UTC),
        analysis_result=cast(
            TrendAnalysisResultLike,
            FakeAnalysisResult(
                outcome="no_significant_trend",
                analysis_version="0.1.0",
                signature=None,
            ),
        ),
        existing_trend=None,
    )

    assert result.outcome_state == "no_op"
    assert result.outcome_reason_code == "no_significant_trend"
    assert repository.record_writes == []
    assert repository.transition_writes == []


def test_insufficient_data_writes_no_lifecycle_rows() -> None:
    """Insufficient-data outcome should be a successful no-op with no writes."""
    repository = FakeTrendRepository()
    service = TrendLifecycleService(repository=repository)

    result = service.apply_analysis_result(
        series_key="SERIES.X",
        latest_observation_on=datetime(2026, 3, 1, tzinfo=UTC),
        analysis_result=cast(
            TrendAnalysisResultLike,
            FakeAnalysisResult(
                outcome="insufficient_data",
                analysis_version="0.1.0",
                signature=None,
            ),
        ),
        existing_trend=None,
    )

    assert result.outcome_state == "no_op"
    assert result.outcome_reason_code == "insufficient_data"
    assert repository.record_writes == []
    assert repository.transition_writes == []
