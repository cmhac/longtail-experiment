"""US1 tests for reversal-event detection from canonical trend transitions."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_runtime_processor import TrendRuntimeProcessor

_EXPECTED_EVENT_COUNT = 2
_EXPECTED_FAN_OUT_COUNT = 2


class _FakeObservationRepository:
    def __init__(self, rows_by_series: dict[str, list[dict[str, object]]]) -> None:
        self._rows_by_series = rows_by_series

    def read_series_observations(self, *, series_key: str) -> list[dict[str, object]]:
        return list(self._rows_by_series.get(series_key, []))


class _FakeNotificationTrendRepository:
    def __init__(
        self,
        *,
        previous_by_series: dict[str, str | None] | None = None,
        active_subscribers_by_series: dict[str, int] | None = None,
        trend_record_count_by_series: dict[str, int] | None = None,
        canonical_count_by_series: dict[str, int] | None = None,
    ) -> None:
        self.applicability_writes: list[dict[str, object]] = []
        self.snapshot_writes: list[dict[str, object]] = []
        self.canonical_writes: list[dict[str, object]] = []
        self.events: list[dict[str, object]] = []
        self.fan_out_calls: list[str] = []
        self.previous_by_series = previous_by_series or {}
        self.active_subscribers_by_series = active_subscribers_by_series or {}
        self.event_series_key_by_id: dict[str, str] = {}
        self.fan_out_results: list[int] = []
        self.trend_record_count_by_series = trend_record_count_by_series or {}
        self.canonical_count_by_series = canonical_count_by_series or {}

    def count_trend_records_for_series(self, *, series_key: str) -> int:
        return self.trend_record_count_by_series.get(series_key, 1)

    def count_canonical_descriptors_for_series(self, *, series_key: str) -> int:
        return self.canonical_count_by_series.get(series_key, 10)

    def upsert_lookback_applicability(self, payload: dict[str, object]) -> None:
        self.applicability_writes.append(dict(payload))

    def upsert_lookback_snapshot(self, payload: dict[str, object]) -> None:
        self.snapshot_writes.append(dict(payload))

    def upsert_canonical_descriptor(self, payload: dict[str, object]) -> None:
        self.canonical_writes.append(dict(payload))

    def get_previous_canonical_direction(
        self,
        *,
        series_key: str,
        observed_on: date,
    ) -> str | None:
        del observed_on
        return self.previous_by_series.get(series_key)

    def append_trend_change_event(self, payload: dict[str, object]) -> dict[str, object]:
        self.events.append(dict(payload))
        event_id = f"event-{len(self.events)}"
        self.event_series_key_by_id[event_id] = str(payload["series_key"])
        return {
            "event_id": event_id,
            "inserted": True,
        }

    def fan_out_notifications_for_event(self, *, event_id: str) -> int:
        self.fan_out_calls.append(event_id)
        series_key = self.event_series_key_by_id[event_id]
        inserted = self.active_subscribers_by_series.get(series_key, 1)
        self.fan_out_results.append(inserted)
        return inserted


def _build_rows_for_direction(direction: str) -> list[dict[str, object]]:
    base: list[dict[str, object]] = [
        {"observed_on": date(2026, 1, 1), "value": 100.0},
        {"observed_on": date(2026, 1, 2), "value": 101.0},
    ]
    if direction == "up":
        base.append({"observed_on": date(2026, 1, 3), "value": 120.0})
    else:
        base.append({"observed_on": date(2026, 1, 3), "value": 80.0})
    return base


def test_us1_creates_event_for_up_to_down_transition() -> None:
    repository = _FakeNotificationTrendRepository(previous_by_series={"SERIES.UP_TO_DOWN": "up"})
    up_to_down_rows: list[dict[str, object]] = _build_rows_for_direction("up") + [
        cast(dict[str, object], {"observed_on": date(2026, 1, 4), "value": 70.0})
    ]
    processor = TrendRuntimeProcessor(
        observation_repository=_FakeObservationRepository(
            {
                "SERIES.UP_TO_DOWN": up_to_down_rows,
            }
        ),
        trend_repository=repository,
    )

    result = processor.process_series(series_key="SERIES.UP_TO_DOWN")

    assert result["execution_state"] in {"applied", "partial_applied"}
    assert len(repository.events) == 1
    event = repository.events[0]
    assert event["previous_direction"] == "up"
    assert event["current_direction"] == "down"
    assert event["processing_context"] == "incremental"
    assert event["visibility_classification"] == "user_visible"
    assert len(repository.fan_out_calls) == 1


def test_us1_creates_event_for_down_to_up_transition() -> None:
    repository = _FakeNotificationTrendRepository(previous_by_series={"SERIES.DOWN_TO_UP": "down"})
    down_to_up_rows: list[dict[str, object]] = _build_rows_for_direction("down") + [
        cast(dict[str, object], {"observed_on": date(2026, 1, 4), "value": 130.0})
    ]
    processor = TrendRuntimeProcessor(
        observation_repository=_FakeObservationRepository(
            {
                "SERIES.DOWN_TO_UP": down_to_up_rows,
            }
        ),
        trend_repository=repository,
    )

    result = processor.process_series(series_key="SERIES.DOWN_TO_UP")

    assert result["execution_state"] in {"applied", "partial_applied"}
    assert len(repository.events) == 1
    event = repository.events[0]
    assert event["previous_direction"] == "down"
    assert event["current_direction"] == "up"
    assert event["processing_context"] == "incremental"


def test_us1_non_event_cases_do_not_create_reversal_event() -> None:
    repository = _FakeNotificationTrendRepository(
        previous_by_series={
            "SERIES.FIRST_AVAILABLE": None,
            "SERIES.UNCHANGED": "up",
        }
    )
    processor = TrendRuntimeProcessor(
        observation_repository=_FakeObservationRepository(
            {
                "SERIES.FIRST_AVAILABLE": [
                    {"observed_on": date(2026, 1, 1), "value": 100.0},
                    {"observed_on": date(2026, 1, 2), "value": 101.0},
                    {"observed_on": date(2026, 1, 3), "value": 102.0},
                ],
                "SERIES.UNCHANGED": [
                    {"observed_on": date(2026, 1, 1), "value": 100.0},
                    {"observed_on": date(2026, 1, 2), "value": 101.0},
                    {"observed_on": date(2026, 1, 3), "value": 103.0},
                    {"observed_on": date(2026, 1, 4), "value": 105.0},
                ],
            }
        ),
        trend_repository=repository,
    )

    first_result = processor.process_series(series_key="SERIES.FIRST_AVAILABLE")
    unchanged_result = processor.process_series(series_key="SERIES.UNCHANGED")

    assert first_result["execution_state"] in {"applied", "partial_applied"}
    assert unchanged_result["execution_state"] in {"applied", "partial_applied"}
    assert len(repository.events) == 0
    assert len(repository.fan_out_calls) == 0


def test_us2_subscription_fan_out_eligibility_uses_active_subscribers_only() -> None:
    repository = _FakeNotificationTrendRepository(
        previous_by_series={
            "SERIES.SUBSCRIBED": "up",
            "SERIES.UNSUBSCRIBED": "up",
        },
        active_subscribers_by_series={
            "SERIES.SUBSCRIBED": 2,
            "SERIES.UNSUBSCRIBED": 0,
        },
    )
    processor = TrendRuntimeProcessor(
        observation_repository=_FakeObservationRepository(
            {
                "SERIES.SUBSCRIBED": [
                    {"observed_on": date(2026, 1, 1), "value": 100.0},
                    {"observed_on": date(2026, 1, 2), "value": 101.0},
                    {"observed_on": date(2026, 1, 3), "value": 70.0},
                ],
                "SERIES.UNSUBSCRIBED": [
                    {"observed_on": date(2026, 1, 1), "value": 100.0},
                    {"observed_on": date(2026, 1, 2), "value": 101.0},
                    {"observed_on": date(2026, 1, 3), "value": 70.0},
                ],
            }
        ),
        trend_repository=repository,
    )

    subscribed = processor.process_series(series_key="SERIES.SUBSCRIBED")
    unsubscribed = processor.process_series(series_key="SERIES.UNSUBSCRIBED")

    assert subscribed["execution_state"] in {"applied", "partial_applied"}
    assert unsubscribed["execution_state"] in {"applied", "partial_applied"}
    assert len(repository.events) == _EXPECTED_EVENT_COUNT
    assert len(repository.fan_out_calls) == _EXPECTED_FAN_OUT_COUNT
    assert sorted(repository.fan_out_results) == [0, 2]


def test_us5_historical_reprocessing_is_audit_only_and_not_fanned_out() -> None:
    repository = _FakeNotificationTrendRepository(
        previous_by_series={
            "SERIES.HISTORICAL": "up",
        },
        trend_record_count_by_series={"SERIES.HISTORICAL": 0},
        canonical_count_by_series={"SERIES.HISTORICAL": 0},
    )
    processor = TrendRuntimeProcessor(
        observation_repository=_FakeObservationRepository(
            {
                "SERIES.HISTORICAL": [
                    {"observed_on": date(2026, 1, 1), "value": 100.0},
                    {"observed_on": date(2026, 1, 2), "value": 101.0},
                    {"observed_on": date(2026, 1, 3), "value": 102.0},
                    {"observed_on": date(2026, 1, 4), "value": 70.0},
                ]
            }
        ),
        trend_repository=repository,
    )

    result = processor.process_series(series_key="SERIES.HISTORICAL")

    assert result["execution_state"] in {"applied", "partial_applied"}
    assert any(
        event["processing_context"] == "historical_reprocessing" for event in repository.events
    )
    assert any(event["visibility_classification"] == "audit_only" for event in repository.events)
    assert repository.fan_out_calls == []
