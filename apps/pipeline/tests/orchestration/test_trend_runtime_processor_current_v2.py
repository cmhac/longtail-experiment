"""US1 integration test for current canonical v2 output propagation."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_runtime_processor import TrendRuntimeProcessor


class _ObsRepo:
    def read_series_observations(self, *, series_key: str):
        del series_key
        return [
            {"observed_on": date(2026, 1, 1), "value": 100.0},
            {"observed_on": date(2026, 1, 2), "value": 101.0},
            {"observed_on": date(2026, 1, 3), "value": 103.0},
            {"observed_on": date(2026, 1, 4), "value": 106.0},
        ]


class _TrendRepo:
    def __init__(self) -> None:
        self.last_canonical = None

    def count_trend_records_for_series(self, *, series_key: str) -> int:
        del series_key
        return 0

    def count_canonical_descriptors_for_series(self, *, series_key: str) -> int:
        del series_key
        return 0

    def upsert_lookback_applicability(self, payload):
        del payload

    def upsert_lookback_snapshot(self, payload):
        del payload

    def upsert_canonical_descriptor(self, payload):
        self.last_canonical = dict(payload)

    def get_previous_canonical_direction(self, *, series_key: str, observed_on: date):
        del series_key, observed_on
        return None

    def append_trend_change_event(self, payload):
        del payload
        return {"event_id": "event-1", "inserted": True}

    def fan_out_notifications_for_event(self, *, event_id: str):
        del event_id
        return 0


def test_runtime_processor_writes_v2_canonical_fields() -> None:
    trend_repo = _TrendRepo()
    processor = TrendRuntimeProcessor(
        observation_repository=_ObsRepo(), trend_repository=trend_repo
    )

    result = processor.process_series(series_key="SERIES.V2")
    assert result["execution_state"] in {"applied", "partial_applied"}
    assert trend_repo.last_canonical is not None
