"""US1 tests for trend notification service idempotent behavior."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Literal, cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_notification_service import TrendNotificationService
from src.orchestration.resources.trend_repository import TrendRepository


class _FakeTrendRepository:
    def __init__(self) -> None:
        self.previous_direction: Literal["up", "down"] | None = "up"
        self.events_by_fingerprint: dict[str, str] = {}
        self.fan_out_calls: list[str] = []
        self.active_subscriber_count = 1

    def get_previous_canonical_direction(
        self,
        *,
        series_key: str,
        observed_on: date,
    ) -> Literal["up", "down"] | None:
        del series_key, observed_on
        return self.previous_direction

    def append_trend_change_event(self, payload: dict[str, object]) -> dict[str, object]:
        fingerprint = str(payload["idempotency_fingerprint"])
        existing = self.events_by_fingerprint.get(fingerprint)
        if existing is not None:
            return {
                "event_id": existing,
                "inserted": False,
            }

        event_id = f"event-{len(self.events_by_fingerprint) + 1}"
        self.events_by_fingerprint[fingerprint] = event_id
        return {
            "event_id": event_id,
            "inserted": True,
        }

    def fan_out_notifications_for_event(self, *, event_id: str) -> int:
        self.fan_out_calls.append(event_id)
        return self.active_subscriber_count


def test_retry_idempotency_uses_single_reversal_event_fingerprint() -> None:
    repository = _FakeTrendRepository()
    service = TrendNotificationService(repository=cast(TrendRepository, repository))

    first = service.process_canonical_transition(
        series_key="PRICE.US.CPI",
        observed_on=date(2026, 1, 2),
        current_direction="down",
        processing_context="incremental",
        visibility_classification="user_visible",
    )
    second = service.process_canonical_transition(
        series_key="PRICE.US.CPI",
        observed_on=date(2026, 1, 2),
        current_direction="down",
        processing_context="incremental",
        visibility_classification="user_visible",
    )

    assert first.inserted is True
    assert second.inserted is False
    assert first.event_id == second.event_id
    assert len(repository.events_by_fingerprint) == 1
    assert len(repository.fan_out_calls) == 2


def test_non_reversal_outcomes_do_not_persist_events() -> None:
    repository = _FakeTrendRepository()
    service = TrendNotificationService(repository=cast(TrendRepository, repository))

    repository.previous_direction = "up"
    unchanged = service.process_canonical_transition(
        series_key="PRICE.US.CPI",
        observed_on=date(2026, 1, 2),
        current_direction="up",
        processing_context="incremental",
        visibility_classification="user_visible",
    )
    repository.previous_direction = None
    first_available = service.process_canonical_transition(
        series_key="PRICE.US.CPI",
        observed_on=date(2026, 1, 3),
        current_direction="down",
        processing_context="incremental",
        visibility_classification="user_visible",
    )
    unavailable = service.process_canonical_transition(
        series_key="PRICE.US.CPI",
        observed_on=date(2026, 1, 4),
        current_direction=None,
        processing_context="incremental",
        visibility_classification="user_visible",
    )

    assert unchanged.outcome_reason_code == "direction_unchanged"
    assert first_available.outcome_reason_code == "no_prior_direction"
    assert unavailable.outcome_reason_code == "direction_unavailable"
    assert len(repository.events_by_fingerprint) == 0
    assert repository.fan_out_calls == []


def test_us2_resubscribe_behavior_is_forward_only() -> None:
    repository = _FakeTrendRepository()
    service = TrendNotificationService(repository=cast(TrendRepository, repository))

    first = service.process_canonical_transition(
        series_key="PRICE.US.CPI",
        observed_on=date(2026, 1, 2),
        current_direction="down",
        processing_context="incremental",
        visibility_classification="user_visible",
    )
    repository.previous_direction = "down"
    repository.active_subscriber_count = 0
    second = service.process_canonical_transition(
        series_key="PRICE.US.CPI",
        observed_on=date(2026, 1, 3),
        current_direction="up",
        processing_context="incremental",
        visibility_classification="user_visible",
    )
    repository.previous_direction = "up"
    repository.active_subscriber_count = 1
    third = service.process_canonical_transition(
        series_key="PRICE.US.CPI",
        observed_on=date(2026, 1, 4),
        current_direction="down",
        processing_context="incremental",
        visibility_classification="user_visible",
    )

    assert first.inserted is True
    assert first.fan_out_count == 1
    assert second.inserted is True
    assert second.fan_out_count == 0
    assert third.inserted is True
    assert third.fan_out_count == 1
