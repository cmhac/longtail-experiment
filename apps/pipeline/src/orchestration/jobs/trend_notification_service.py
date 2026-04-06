"""Service for detecting and persisting reversal notification events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Literal

from ..resources.trend_repository import TrendRepository


@dataclass(frozen=True)
class TrendNotificationApplyResult:
    """Outcome metadata for one potential reversal event."""

    outcome_reason_code: str
    event_id: str | None
    inserted: bool
    fan_out_count: int


class TrendNotificationService:
    """Detect canonical up/down reversals and persist notification events."""

    def __init__(self, *, repository: TrendRepository) -> None:
        self._repository = repository

    def process_canonical_transition(
        self,
        *,
        series_key: str,
        observed_on: date,
        current_direction: Literal["up", "down"] | None,
        processing_context: Literal["incremental", "historical_reprocessing"],
        visibility_classification: Literal["user_visible", "audit_only"],
    ) -> TrendNotificationApplyResult:
        """Persist one reversal event when prior/current canonical directions qualify."""

        if current_direction not in {"up", "down"}:
            return TrendNotificationApplyResult(
                outcome_reason_code="direction_unavailable",
                event_id=None,
                inserted=False,
                fan_out_count=0,
            )

        previous_direction = self._repository.get_previous_canonical_direction(
            series_key=series_key,
            observed_on=observed_on,
        )
        if previous_direction is None:
            return TrendNotificationApplyResult(
                outcome_reason_code="no_prior_direction",
                event_id=None,
                inserted=False,
                fan_out_count=0,
            )
        if previous_direction == current_direction:
            return TrendNotificationApplyResult(
                outcome_reason_code="direction_unchanged",
                event_id=None,
                inserted=False,
                fan_out_count=0,
            )

        idempotency_fingerprint = (
            f"{series_key}|{observed_on.isoformat()}|{previous_direction}|"
            f"{current_direction}|{processing_context}"
        )
        persisted = self._repository.append_trend_change_event(
            {
                "series_key": series_key,
                "previous_direction": previous_direction,
                "current_direction": current_direction,
                "effective_observed_on": observed_on,
                "processing_context": processing_context,
                "visibility_classification": visibility_classification,
                "idempotency_fingerprint": idempotency_fingerprint,
                "emitted_at": datetime.now(tz=UTC),
            }
        )
        event_id = str(persisted["event_id"])

        fan_out_count = 0
        if visibility_classification == "user_visible":
            fan_out_count = self._repository.fan_out_notifications_for_event(event_id=event_id)

        return TrendNotificationApplyResult(
            outcome_reason_code="reversal_event_recorded",
            event_id=event_id,
            inserted=bool(persisted["inserted"]),
            fan_out_count=fan_out_count,
        )
