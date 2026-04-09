"""US2 as-of snapshot reproducibility checks for v2 payload ordering."""

# ruff: noqa: D103

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
            {"observed_on": date(2026, 1, 5), "value": 110.0},
        ]


class _TrendRepo:
    def __init__(self) -> None:
        self.canonical_payloads = []

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
        self.canonical_payloads.append(dict(payload))

    def get_previous_canonical_direction(self, *, series_key: str, observed_on: date):
        del series_key, observed_on

    def append_trend_change_event(self, payload):
        del payload
        return {"event_id": "event-1", "inserted": True}

    def fan_out_notifications_for_event(self, *, event_id: str):
        del event_id
        return 0


def test_asof_v2_canonical_payloads_are_reproducible_across_runs() -> None:
    trend_repo = _TrendRepo()
    processor = TrendRuntimeProcessor(
        observation_repository=_ObsRepo(), trend_repository=trend_repo
    )

    processor.process_series(series_key="SERIES.ASOF")
    first = list(trend_repo.canonical_payloads)
    trend_repo.canonical_payloads.clear()
    processor.process_series(series_key="SERIES.ASOF")
    second = list(trend_repo.canonical_payloads)

    assert first == second
