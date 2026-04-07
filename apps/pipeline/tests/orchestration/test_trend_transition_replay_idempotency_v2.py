"""US3 tests for replay/backfill visibility and idempotent event behavior."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_notification_service import TrendNotificationService
from src.orchestration.resources.trend_repository import TrendRepository


class _ReplayRepository:
    def __init__(self) -> None:
        self.previous_direction: str | None = "up"
        self.events_by_fingerprint: dict[str, str] = {}
        self.fan_out_calls: list[str] = []

    def get_previous_canonical_direction(self, *, series_key: str, observed_on: date) -> str | None:
        del series_key, observed_on
        return self.previous_direction

    def append_trend_change_event(self, payload: dict[str, object]) -> dict[str, object]:
        fingerprint = str(payload["idempotency_fingerprint"])
        if fingerprint in self.events_by_fingerprint:
            return {"event_id": self.events_by_fingerprint[fingerprint], "inserted": False}
        event_id = f"event-{len(self.events_by_fingerprint) + 1}"
        self.events_by_fingerprint[fingerprint] = event_id
        return {"event_id": event_id, "inserted": True}

    def fan_out_notifications_for_event(self, *, event_id: str) -> int:
        self.fan_out_calls.append(event_id)
        return 1


def test_incremental_replay_keeps_event_idempotent_with_single_fingerprint() -> None:
    repository = _ReplayRepository()
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


def test_historical_reprocessing_events_are_audit_only_without_user_fanout() -> None:
    repository = _ReplayRepository()
    service = TrendNotificationService(repository=cast(TrendRepository, repository))

    result = service.process_canonical_transition(
        series_key="PRICE.US.CPI",
        observed_on=date(2026, 1, 2),
        current_direction="down",
        processing_context="historical_reprocessing",
        visibility_classification="audit_only",
    )

    assert result.inserted is True
    assert result.fan_out_count == 0
    assert repository.fan_out_calls == []
