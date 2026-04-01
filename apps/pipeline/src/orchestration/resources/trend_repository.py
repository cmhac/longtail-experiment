"""Structural contracts for trend lifecycle persistence resources."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, TypedDict


class TrendRecordInsert(TypedDict):
    """Values needed to persist one lifecycle trend record."""

    series_key: str
    trend_label: str
    direction: str
    strength: str
    seasonality_classification: str
    start_period: datetime
    end_period: datetime | None
    is_ongoing: bool


class TrendTransitionInsert(TypedDict):
    """Values needed to persist one lifecycle transition event."""

    series_key: str
    transition_type: str
    prior_trend_record_id: str | None
    new_trend_record_id: str | None
    trigger_observation_on: datetime
    reason: str


class TrendRepository(Protocol):
    """Persistence contract for trend lifecycle records/events."""

    def get_ongoing_trend_for_series(self, *, series_key: str) -> dict[str, object] | None:
        """Return current ongoing trend snapshot for one series, if present."""

    def upsert_trend_record(self, payload: TrendRecordInsert) -> str:
        """Insert or update one trend record and return canonical record id."""

    def close_ongoing_trend_for_series(
        self,
        *,
        series_key: str,
        end_period: datetime,
    ) -> str | None:
        """Mark the current ongoing trend as ended and return its id when present."""

    def append_transition(self, payload: TrendTransitionInsert) -> None:
        """Persist one transition event for auditing and downstream visibility."""

    def count_trend_records_for_series(self, *, series_key: str) -> int:
        """Return persisted trend record count for one canonical series key."""
