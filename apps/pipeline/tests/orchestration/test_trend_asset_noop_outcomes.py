"""US1 integration-like tests for lookback no-op and partial outcomes."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_lifecycle_service import TrendLifecycleService
from src.orchestration.resources.trend_repository import TrendRepository


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


@dataclass(frozen=True)
class FakeCadenceDecision:
    """Minimal cadence decision fixture."""

    cadence_state: str
    inferred_cadence: str | None
    irregular_gap_count: int
    total_interval_count: int
    irregular_gap_ratio: float
    reason_code: str
    reason_detail: str | None


@dataclass(frozen=True)
class FakeLookbackEvaluation:
    """Minimal lookback evaluation payload fixture."""

    applicability: tuple[object, ...]
    lookback_snapshots: tuple[object, ...]
    canonical_descriptor: object
    cadence_decision: object


class FakeTrendRepository(TrendRepository):
    """Collect repository writes for assertion-friendly lifecycle tests."""

    def __init__(self, *, fail_snapshot_writes: bool = False) -> None:
        """Initialize write buffers and optional snapshot failure mode."""
        self.fail_snapshot_writes = fail_snapshot_writes
        self.applicability_writes: list[dict[str, object]] = []
        self.snapshot_writes: list[dict[str, object]] = []
        self.canonical_writes: list[dict[str, object]] = []

    def upsert_trend_record(self, payload):
        """Legacy lifecycle method is intentionally unused for lookback tests."""
        raise NotImplementedError

    def append_transition(self, payload):
        """Legacy lifecycle method is intentionally unused for lookback tests."""
        raise NotImplementedError

    def upsert_lookback_applicability(self, payload):
        """Collect one lookback applicability write."""
        self.applicability_writes.append(dict(payload))

    def upsert_lookback_snapshot(self, payload):
        """Collect one lookback snapshot write or simulate failure."""
        if self.fail_snapshot_writes:
            raise RuntimeError("snapshot failed")
        self.snapshot_writes.append(dict(payload))

    def upsert_canonical_descriptor(self, payload):
        """Collect one canonical descriptor write."""
        self.canonical_writes.append(dict(payload))


def test_no_significant_lookbacks_still_persist_with_unavailable_canonical() -> None:
    """No-significant lookback state should persist and return applied metadata."""
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
                outcome_state="no_significant_trend",
                trend_label=None,
                direction=None,
                strength=None,
                seasonality_classification=None,
                analysis_version="0.1.0",
            ),
        ),
        canonical_descriptor=FakeCanonicalResult(
            descriptor_state="unavailable",
            weighting_version="1.0.0",
            trend_label=None,
            direction=None,
            strength=None,
            selected_lookback_points=None,
            weighting_trace={"selected": None},
        ),
        cadence_decision=FakeCadenceDecision(
            cadence_state="regular",
            inferred_cadence="daily",
            irregular_gap_count=0,
            total_interval_count=7,
            irregular_gap_ratio=0.0,
            reason_code="regular_spacing",
            reason_detail=None,
        ),
    )

    result = service.apply_lookback_evaluation(
        series_key="SERIES.X",
        observed_on=date(2026, 3, 1),
        observation_id=None,
        evaluation_result=cast(object, evaluation),
    )

    assert result.outcome_state == "applied"
    assert result.outcome_reason_code == "lookback_snapshots_persisted"
    assert result.cadence_decision is not None
    assert result.cadence_decision["cadence_state"] == "regular"
    assert len(repository.applicability_writes) == 1
    assert len(repository.snapshot_writes) == 1
    assert len(repository.canonical_writes) == 1


def test_snapshot_write_failure_returns_partial_applied() -> None:
    """Snapshot write errors should not block canonical writes for same observation."""
    repository = FakeTrendRepository(fail_snapshot_writes=True)
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
        cadence_decision=FakeCadenceDecision(
            cadence_state="gap_tolerant",
            inferred_cadence="weekly",
            irregular_gap_count=1,
            total_interval_count=500,
            irregular_gap_ratio=0.002,
            reason_code="isolated_irregular_gaps_tolerated",
            reason_detail="ratio=0.002000,threshold=0.002000",
        ),
    )

    result = service.apply_lookback_evaluation(
        series_key="SERIES.X",
        observed_on=date(2026, 3, 1),
        observation_id=None,
        evaluation_result=cast(object, evaluation),
    )

    assert result.outcome_state == "partial_applied"
    assert result.outcome_reason_code == "partial_lookback_write_failure"
    assert result.cadence_decision is not None
    assert result.cadence_decision["cadence_state"] == "gap_tolerant"
    assert len(repository.applicability_writes) == 1
    assert len(repository.canonical_writes) == 1
