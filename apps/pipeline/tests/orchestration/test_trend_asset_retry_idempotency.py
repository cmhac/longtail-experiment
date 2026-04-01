"""US1 tests for state-based idempotency in trend lifecycle writes."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_lifecycle_service import TrendLifecycleService
from src.orchestration.resources.trend_repository import TrendRepository

EXPECTED_RETRY_WRITES = 2


@dataclass(frozen=True)
class FakeLookbackEvaluation:
    """Minimal lookback evaluation shape used by lifecycle service tests."""

    applicability: tuple[object, ...]
    lookback_snapshots: tuple[object, ...]
    canonical_descriptor: object


@dataclass(frozen=True)
class FakeLookbackApplicability:
    """Minimal applicability row fixture."""

    lookback_points: int
    applicability_state: str
    reason_code: str
    reason_detail: str | None


@dataclass(frozen=True)
class FakeLookbackSnapshot:
    """Minimal lookback snapshot fixture."""

    lookback_points: int
    outcome_state: str
    trend_label: str | None
    direction: str | None
    strength: str | None
    seasonality_classification: str | None
    analysis_version: str


@dataclass(frozen=True)
class FakeCanonicalResult:
    """Minimal canonical descriptor fixture."""

    descriptor_state: str
    weighting_version: str
    trend_label: str | None
    direction: str | None
    strength: str | None
    selected_lookback_points: int | None
    weighting_trace: dict[str, object] | None


class FakeTrendRepository(TrendRepository):
    """Collect repository writes for idempotency assertions."""

    def __init__(self) -> None:
        """Initialize empty write-collection buffers for assertions."""
        self.record_writes: list[dict[str, object]] = []
        self.transition_writes: list[dict[str, object]] = []
        self.applicability_writes: list[dict[str, object]] = []
        self.snapshot_writes: list[dict[str, object]] = []
        self.canonical_writes: list[dict[str, object]] = []

    def upsert_trend_record(self, payload):
        """Collect one trend record write and return a stable fake id."""
        self.record_writes.append(dict(payload))
        return "trend-record-id"

    def append_transition(self, payload):
        """Collect one transition write for downstream assertions."""
        self.transition_writes.append(dict(payload))

    def upsert_lookback_applicability(self, payload):
        """Collect one lookback applicability write."""
        self.applicability_writes.append(dict(payload))

    def upsert_lookback_snapshot(self, payload):
        """Collect one lookback snapshot write."""
        self.snapshot_writes.append(dict(payload))

    def upsert_canonical_descriptor(self, payload):
        """Collect one canonical descriptor write."""
        self.canonical_writes.append(dict(payload))


def test_retry_with_unchanged_state_is_idempotent_and_writes_nothing() -> None:
    """Repeated processing for unchanged lookback state must upsert same logical rows."""
    repository = FakeTrendRepository()
    service = TrendLifecycleService(repository=repository)

    evaluation = FakeLookbackEvaluation(
        applicability=(
            FakeLookbackApplicability(
                lookback_points=1,
                applicability_state="applicable",
                reason_code="applicable",
                reason_detail=None,
            ),
        ),
        lookback_snapshots=(
            FakeLookbackSnapshot(
                lookback_points=1,
                outcome_state="significant_trend",
                trend_label="mild_sustained_uptrend",
                direction="up",
                strength="mild",
                seasonality_classification="non_seasonal",
                analysis_version="0.1.0",
            ),
        ),
        canonical_descriptor=FakeCanonicalResult(
            descriptor_state="available",
            weighting_version="1.0.0",
            trend_label="mild_sustained_uptrend",
            direction="up",
            strength="mild",
            selected_lookback_points=1,
            weighting_trace={"selected": 1},
        ),
    )

    first = service.apply_lookback_evaluation(
        series_key="SERIES.IDEMPOTENT",
        observed_on=date(2026, 3, 1),
        observation_id=None,
        evaluation_result=cast(object, evaluation),
    )
    second = service.apply_lookback_evaluation(
        series_key="SERIES.IDEMPOTENT",
        observed_on=date(2026, 3, 1),
        observation_id=None,
        evaluation_result=cast(object, evaluation),
    )

    assert first.outcome_state == "applied"
    assert first.outcome_reason_code == "lookback_snapshots_persisted"
    assert second.outcome_state == "applied"
    assert second.outcome_reason_code == "lookback_snapshots_persisted"
    assert len(repository.applicability_writes) == EXPECTED_RETRY_WRITES
    assert len(repository.snapshot_writes) == EXPECTED_RETRY_WRITES
    assert len(repository.canonical_writes) == EXPECTED_RETRY_WRITES
