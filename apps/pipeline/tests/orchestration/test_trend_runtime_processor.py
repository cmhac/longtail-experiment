"""Runtime trend processing integration tests for ingest execution."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_runtime_processor import TrendRuntimeProcessor

EXPECTED_LOOKBACK_COUNT = 12
ELIGIBLE_BACKFILL_OBSERVATION_COUNT = 4


class _FakeObservationRepository:
    def __init__(self, rows_by_series: dict[str, list[dict[str, object]]]) -> None:
        self._rows_by_series = rows_by_series

    def read_series_observations(self, *, series_key: str) -> list[dict[str, object]]:
        return list(self._rows_by_series.get(series_key, []))


class _FakeTrendRepository:
    def __init__(
        self,
        *,
        trend_record_count: int = 0,
        canonical_descriptor_count: int = 0,
    ) -> None:
        self.trend_record_count = trend_record_count
        self.canonical_descriptor_count = canonical_descriptor_count
        self.applicability_writes: list[dict[str, object]] = []
        self.snapshot_writes: list[dict[str, object]] = []
        self.canonical_writes: list[dict[str, object]] = []

    def count_trend_records_for_series(self, *, series_key: str) -> int:
        del series_key
        return self.trend_record_count

    def count_canonical_descriptors_for_series(self, *, series_key: str) -> int:
        del series_key
        return self.canonical_descriptor_count

    def upsert_lookback_applicability(self, payload: dict[str, object]) -> None:
        self.applicability_writes.append(dict(payload))

    def upsert_lookback_snapshot(self, payload: dict[str, object]) -> None:
        self.snapshot_writes.append(dict(payload))

    def upsert_canonical_descriptor(self, payload: dict[str, object]) -> None:
        self.canonical_writes.append(dict(payload))


def test_first_run_persists_lookback_rows() -> None:
    """First run with sufficient history should persist applicability/snapshot rows."""
    series_key = "SERIES.UP"
    rows: list[dict[str, object]] = cast(
        list[dict[str, object]],
        [{"observed_on": date(2026, 1, day), "value": float(day)} for day in (1, 2, 3, 4, 5, 6)],
    )
    trend_repository = _FakeTrendRepository()
    processor = TrendRuntimeProcessor(
        observation_repository=_FakeObservationRepository({series_key: rows}),
        trend_repository=trend_repository,
    )

    result = processor.process_series(series_key=series_key)

    assert result["execution_state"] == "applied"
    assert result["outcome_reason_code"] == "lookback_snapshots_persisted"
    # Eligible observations exclude first two points (cadence inference needs 3 points).
    assert (
        len(trend_repository.applicability_writes)
        == EXPECTED_LOOKBACK_COUNT * ELIGIBLE_BACKFILL_OBSERVATION_COUNT
    )
    assert len(trend_repository.snapshot_writes) >= 1
    assert len(trend_repository.canonical_writes) == ELIGIBLE_BACKFILL_OBSERVATION_COUNT


def test_empty_series_is_noop() -> None:
    """No observations should return explicit no-op metadata."""
    processor = TrendRuntimeProcessor(
        observation_repository=_FakeObservationRepository({"SERIES.EMPTY": []}),
        trend_repository=_FakeTrendRepository(),
    )

    result = processor.process_series(series_key="SERIES.EMPTY")

    assert result["execution_state"] == "no_op"
    assert result["outcome_reason_code"] == "no_observations"


def test_existing_series_with_partial_canonical_history_triggers_backfill() -> None:
    """Existing trend records should still backfill when canonical history is incomplete."""
    series_key = "SERIES.PARTIAL_HISTORY"
    rows: list[dict[str, object]] = cast(
        list[dict[str, object]],
        [{"observed_on": date(2026, 1, day), "value": float(day)} for day in (1, 2, 3, 4, 5, 6)],
    )
    trend_repository = _FakeTrendRepository(trend_record_count=1, canonical_descriptor_count=1)
    processor = TrendRuntimeProcessor(
        observation_repository=_FakeObservationRepository({series_key: rows}),
        trend_repository=trend_repository,
    )

    result = processor.process_series(series_key=series_key)

    assert result["execution_state"] == "applied"
    assert len(trend_repository.canonical_writes) == ELIGIBLE_BACKFILL_OBSERVATION_COUNT
