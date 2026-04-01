"""Runtime trend processing integration tests for ingest execution."""

from __future__ import annotations

import sys
from datetime import UTC, date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_runtime_processor import TrendRuntimeProcessor


class _FakeObservationRepository:
    def __init__(self, rows_by_series: dict[str, list[dict[str, object]]]) -> None:
        self._rows_by_series = rows_by_series

    def read_series_observations(self, *, series_key: str) -> list[dict[str, object]]:
        return list(self._rows_by_series.get(series_key, []))


class _FakeTrendRepository:
    def __init__(self) -> None:
        self._records: dict[str, dict[str, object]] = {}
        self._ongoing_by_series: dict[str, str] = {}
        self._transitions: list[dict[str, object]] = []

    def get_ongoing_trend_for_series(self, *, series_key: str) -> dict[str, object] | None:
        row_id = self._ongoing_by_series.get(series_key)
        if row_id is None:
            return None
        return dict(self._records[row_id])

    def upsert_trend_record(self, payload: dict[str, object]) -> str:
        record_id = f"record-{len(self._records) + 1}"
        row = {
            "id": record_id,
            "trend_label": payload["trend_label"],
            "direction": payload["direction"],
            "strength": payload["strength"],
            "seasonality_classification": payload["seasonality_classification"],
            "is_ongoing": payload["is_ongoing"],
            "start_period": payload["start_period"],
            "end_period": payload["end_period"],
            "series_key": payload["series_key"],
        }
        self._records[record_id] = row
        if bool(payload["is_ongoing"]):
            self._ongoing_by_series[str(payload["series_key"])] = record_id
        return record_id

    def close_ongoing_trend_for_series(
        self,
        *,
        series_key: str,
        end_period: datetime,
    ) -> str | None:
        row_id = self._ongoing_by_series.pop(series_key, None)
        if row_id is None:
            return None
        row = self._records[row_id]
        row["end_period"] = end_period
        row["is_ongoing"] = False
        return row_id

    def append_transition(self, payload: dict[str, object]) -> None:
        self._transitions.append(dict(payload))

    def count_trend_records_for_series(self, *, series_key: str) -> int:
        return sum(1 for row in self._records.values() if row["series_key"] == series_key)


def test_first_run_backfill_writes_lifecycle_rows() -> None:
    """First run with sufficient history should execute backfill lifecycle writes."""
    series_key = "SERIES.UP"
    rows: list[dict[str, object]] = [
        {"observed_on": date(2026, 1, day), "value": float(day)} for day in (1, 2, 3, 4, 5, 6)
    ]
    processor = TrendRuntimeProcessor(
        observation_repository=_FakeObservationRepository({series_key: rows}),
        trend_repository=_FakeTrendRepository(),
    )

    result = processor.process_series(series_key=series_key)

    assert result["outcome_reason_code"] == "first_run_full_backfill"


def test_existing_trends_use_incremental_processing() -> None:
    """Series with existing trends should use incremental processing branch."""
    series_key = "SERIES.UP"
    rows: list[dict[str, object]] = [
        {"observed_on": date(2026, 1, day), "value": float(day)} for day in (1, 2, 3, 4, 5, 6)
    ]
    trend_repository = _FakeTrendRepository()
    trend_repository.upsert_trend_record(
        {
            "series_key": series_key,
            "trend_label": "strong_sustained_uptrend",
            "direction": "up",
            "strength": "strong",
            "seasonality_classification": "non_seasonal",
            "start_period": datetime(2026, 1, 6, tzinfo=UTC),
            "end_period": None,
            "is_ongoing": True,
        }
    )

    processor = TrendRuntimeProcessor(
        observation_repository=_FakeObservationRepository({series_key: rows}),
        trend_repository=trend_repository,
    )

    result = processor.process_series(series_key=series_key)

    assert result["outcome_reason_code"] in {
        "trend_signature_unchanged",
        "trend_signature_changed",
        "analysis_version_changed",
    }
