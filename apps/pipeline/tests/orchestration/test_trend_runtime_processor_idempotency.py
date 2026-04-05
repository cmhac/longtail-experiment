"""US1 tests for lookback idempotency and partial-failure isolation."""

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


class _IdempotentTrendRepository:
    def __init__(self, *, fail_on_lookback: int | None = None) -> None:
        self.fail_on_lookback = fail_on_lookback
        self.applicability_by_key: dict[tuple[str, date, int], dict[str, object]] = {}
        self.snapshots_by_key: dict[tuple[str, date, int], dict[str, object]] = {}
        self.canonical_by_key: dict[tuple[str, date], dict[str, object]] = {}

    def upsert_lookback_applicability(self, payload: dict[str, object]) -> None:
        key = (
            str(payload["series_key"]),
            cast(date, payload["observed_on"]),
            int(cast(int, payload["lookback_points"])),
        )
        self.applicability_by_key[key] = dict(payload)

    def upsert_lookback_snapshot(self, payload: dict[str, object]) -> None:
        lookback = int(cast(int, payload["lookback_points"]))
        if self.fail_on_lookback == lookback:
            raise RuntimeError("simulated lookback failure")
        key = (str(payload["series_key"]), cast(date, payload["observed_on"]), lookback)
        self.snapshots_by_key[key] = dict(payload)

    def upsert_canonical_descriptor(self, payload: dict[str, object]) -> None:
        key = (str(payload["series_key"]), cast(date, payload["observed_on"]))
        self.canonical_by_key[key] = dict(payload)

    def count_trend_records_for_series(self, *, series_key: str) -> int:
        del series_key
        return 0

    def count_canonical_descriptors_for_series(self, *, series_key: str) -> int:
        return len([key for key in self.canonical_by_key if key[0] == series_key])


def _build_rows() -> list[dict[str, object]]:
    return [
        {"observed_on": date(2026, 1, day), "value": float(100 + day)}
        for day in (1, 2, 3, 4, 5, 6, 7, 8)
    ]


def test_retry_processing_is_idempotent_for_lookback_and_canonical_writes() -> None:
    """Retrying unchanged observation inputs should not create duplicate logical rows."""
    series_key = "SERIES.IDEMPOTENT"
    trend_repository = _IdempotentTrendRepository()
    processor = TrendRuntimeProcessor(
        observation_repository=_FakeObservationRepository({series_key: _build_rows()}),
        trend_repository=trend_repository,
    )

    first = processor.process_series(series_key=series_key)
    second = processor.process_series(series_key=series_key)

    assert first["execution_state"] == "applied"
    assert second["execution_state"] == "applied"
    assert first["cadence_decision"] == second["cadence_decision"]
    assert (
        len(trend_repository.applicability_by_key)
        == EXPECTED_LOOKBACK_COUNT * ELIGIBLE_BACKFILL_OBSERVATION_COUNT
    )
    assert len(trend_repository.snapshots_by_key) > 0
    assert len(trend_repository.canonical_by_key) == ELIGIBLE_BACKFILL_OBSERVATION_COUNT


def test_partial_failure_in_one_lookback_does_not_block_other_writes() -> None:
    """One lookback write failure should not prevent other lookbacks from persisting."""
    series_key = "SERIES.PARTIAL"
    trend_repository = _IdempotentTrendRepository(fail_on_lookback=2)
    processor = TrendRuntimeProcessor(
        observation_repository=_FakeObservationRepository({series_key: _build_rows()}),
        trend_repository=trend_repository,
    )

    result = processor.process_series(series_key=series_key)

    assert result["execution_state"] == "partial_applied"
    assert (
        len(trend_repository.applicability_by_key)
        == EXPECTED_LOOKBACK_COUNT * ELIGIBLE_BACKFILL_OBSERVATION_COUNT
    )
    persisted_lookbacks = {key[2] for key in trend_repository.snapshots_by_key}
    assert 1 in persisted_lookbacks
