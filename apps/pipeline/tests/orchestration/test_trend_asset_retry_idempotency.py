"""US1 tests for state-based idempotency in trend lifecycle writes."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_lifecycle_service import (
    PersistedTrendSnapshot,
    TrendLifecycleService,
)
from src.orchestration.jobs.trend_transition_logic import TrendAnalysisResultLike
from src.orchestration.resources.trend_repository import TrendRepository


@dataclass(frozen=True)
class FakeAnalysisResult:
    """Minimal trend-analysis result shape used by lifecycle service tests."""

    outcome: Literal["significant_trend", "no_significant_trend", "insufficient_data"]
    analysis_version: str
    signature: dict[str, str] | None


class FakeTrendRepository(TrendRepository):
    """Collect repository writes for idempotency assertions."""

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


def test_retry_with_unchanged_state_is_idempotent_and_writes_nothing() -> None:
    """Repeated processing for unchanged persisted state must not add lifecycle rows."""
    repository = FakeTrendRepository()
    service = TrendLifecycleService(repository=repository)

    existing = PersistedTrendSnapshot(
        trend_record_id="existing-record",
        trend_label="mild_sustained_uptrend",
        direction="up",
        strength="mild",
        seasonality_classification="non_seasonal",
        analysis_version="0.1.0",
    )

    result = service.apply_analysis_result(
        series_key="SERIES.IDEMPOTENT",
        latest_observation_on=datetime(2026, 3, 1, tzinfo=UTC),
        analysis_result=cast(
            TrendAnalysisResultLike,
            FakeAnalysisResult(
                outcome="significant_trend",
                analysis_version="0.1.0",
                signature={
                    "trend_label": "mild_sustained_uptrend",
                    "direction": "up",
                    "strength": "mild",
                    "seasonality_classification": "non_seasonal",
                },
            ),
        ),
        existing_trend=existing,
    )

    assert result.outcome_state == "no_op"
    assert result.outcome_reason_code == "trend_signature_unchanged"
    assert repository.record_writes == []
    assert repository.transition_writes == []
