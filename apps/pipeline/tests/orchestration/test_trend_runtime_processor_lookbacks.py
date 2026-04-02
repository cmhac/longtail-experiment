"""US1 tests for lookback applicability and no-signal persistence behavior."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_runtime_processor import TrendRuntimeProcessor

EXPECTED_LOOKBACK_COUNT = 12
ELIGIBLE_BACKFILL_OBSERVATION_COUNT = 6


class _FakeObservationRepository:
    def __init__(self, rows_by_series: dict[str, list[dict[str, object]]]) -> None:
        self._rows_by_series = rows_by_series

    def read_series_observations(self, *, series_key: str) -> list[dict[str, object]]:
        return list(self._rows_by_series.get(series_key, []))


class _FakeTrendRepository:
    def __init__(self) -> None:
        self.applicability_writes: list[dict[str, object]] = []
        self.snapshot_writes: list[dict[str, object]] = []
        self.canonical_writes: list[dict[str, object]] = []

    def upsert_lookback_applicability(self, payload: dict[str, object]) -> None:
        self.applicability_writes.append(dict(payload))

    def upsert_lookback_snapshot(self, payload: dict[str, object]) -> None:
        self.snapshot_writes.append(dict(payload))

    def upsert_canonical_descriptor(self, payload: dict[str, object]) -> None:
        self.canonical_writes.append(dict(payload))

    def count_trend_records_for_series(self, *, series_key: str) -> int:
        del series_key
        return 0

    def count_canonical_descriptors_for_series(self, *, series_key: str) -> int:
        del series_key
        return 0


def test_runtime_persists_applicability_for_supported_and_unsupported_lookbacks() -> None:
    """Processor should persist explicit applicability decisions for the full catalog."""
    series_key = "SERIES.LOOKBACKS"
    rows = [
        {"observed_on": date(2026, 1, day), "value": float(100 + day)}
        for day in (1, 2, 3, 4, 5, 6, 7, 8)
    ]
    typed_rows = cast(list[dict[str, object]], rows)
    trend_repository = _FakeTrendRepository()
    processor = TrendRuntimeProcessor(
        observation_repository=_FakeObservationRepository({series_key: typed_rows}),
        trend_repository=trend_repository,
    )

    result = processor.process_series(series_key=series_key)

    assert result["execution_state"] == "applied"
    assert (
        len(trend_repository.applicability_writes)
        == EXPECTED_LOOKBACK_COUNT * ELIGIBLE_BACKFILL_OBSERVATION_COUNT
    )
    by_lookback = {
        int(cast(int, row["lookback_points"])): row for row in trend_repository.applicability_writes
    }
    assert by_lookback[1]["applicability_state"] == "applicable"
    assert by_lookback[10]["applicability_state"] == "inapplicable"


def test_runtime_persists_no_signal_snapshot_and_unavailable_canonical() -> None:
    """No-signal applicable lookbacks should persist snapshot rows and unavailable canonical."""
    series_key = "SERIES.FLAT"
    rows = [
        {"observed_on": date(2026, 1, day), "value": value}
        for day, value in (
            (1, 100.0),
            (2, 100.1),
            (3, 100.0),
            (4, 100.1),
            (5, 100.0),
            (6, 100.1),
            (7, 100.0),
            (8, 100.1),
        )
    ]
    typed_rows = cast(list[dict[str, object]], rows)
    trend_repository = _FakeTrendRepository()
    processor = TrendRuntimeProcessor(
        observation_repository=_FakeObservationRepository({series_key: typed_rows}),
        trend_repository=trend_repository,
    )

    result = processor.process_series(series_key=series_key)

    assert result["execution_state"] == "applied"
    assert all(
        row["outcome_state"] == "no_significant_trend" for row in trend_repository.snapshot_writes
    )
    assert len(trend_repository.canonical_writes) == ELIGIBLE_BACKFILL_OBSERVATION_COUNT
    assert trend_repository.canonical_writes[-1]["descriptor_state"] == "unavailable"
