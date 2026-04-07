"""Trend notification orchestration service for backend request handlers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from src.contract.errors import ContractQueryError
from src.contract.query.trend_notification_query import (
    DeleteSubscriptionResponse,
    MarkAllReadResponse,
    MarkReadResponse,
    MarkUnreadResponse,
    NotificationListResponse,
    NotificationSummaryResponse,
    SubscriptionListResponse,
    SubscriptionResponse,
)

NOTIFICATION_CONFIDENCE_SCORE_THRESHOLD = 0.70


def _format_notification_body(
    *, dataset_id: str, previous: str, current: str, confidence: float | None
) -> str:
    """Format direction-first notification copy with optional confidence detail."""

    base = f"{dataset_id}: {previous} to {current}"
    if confidence is None or confidence < NOTIFICATION_CONFIDENCE_SCORE_THRESHOLD:
        return base
    return f"{base} (confidence {confidence:.2f})"


class TrendNotificationServiceRepository(Protocol):
    """Repository contract consumed by trend notification service workflows."""

    def list_notifications(
        self,
        *,
        user_id: str,
        page_size: int,
        cursor: str | None,
        unread_only: bool,
    ) -> dict[str, object]:
        """Return one newest-first paginated notification payload."""
        ...

    def get_unread_summary(self, *, user_id: str) -> dict[str, object]:
        """Return unread summary payload for one user."""
        ...

    def mark_notification_read(self, *, user_id: str, notification_id: str) -> bool:
        """Mark one notification read for one user."""
        ...

    def mark_notification_unread(self, *, user_id: str, notification_id: str) -> bool:
        """Mark one notification unread for one user."""
        ...

    def mark_all_notifications_read(self, *, user_id: str) -> int:
        """Mark all unread notifications read for one user."""
        ...

    def list_active_subscriptions(self, *, user_id: str) -> list[dict[str, object]]:
        """Return active dataset subscriptions for one user."""
        ...

    def create_or_reactivate_subscription(
        self,
        *,
        user_id: str,
        dataset_id: str,
    ) -> dict[str, object] | None:
        """Create or reactivate one dataset subscription."""
        ...

    def remove_active_subscription(self, *, user_id: str, dataset_id: str) -> bool:
        """Remove one active dataset subscription when present."""
        ...


@dataclass(slots=True)
class TrendNotificationService:
    """Coordinate trend notification reads and state mutations."""

    repository: TrendNotificationServiceRepository

    def list_notifications(
        self,
        *,
        user_id: str,
        page_size: int | None,
        cursor: str | None,
        unread_only: bool,
    ) -> NotificationListResponse:
        """Return one paginated newest-first notification listing for user."""

        resolved_page_size = 25 if page_size is None else page_size
        if resolved_page_size < 1 or resolved_page_size > 100:
            raise ContractQueryError("page_size must be between 1 and 100")

        payload = self.repository.list_notifications(
            user_id=user_id,
            page_size=resolved_page_size,
            cursor=cursor,
            unread_only=unread_only,
        )

        raw_items = payload.get("items")
        if isinstance(raw_items, list):
            normalized_items: list[dict[str, object]] = []
            for raw_item in raw_items:
                if not isinstance(raw_item, dict):
                    normalized_items.append({})
                    continue
                item = dict(raw_item)
                dataset_id = str(item.get("dataset_id", ""))
                previous = str(item.get("previous_direction", ""))
                current = str(item.get("current_direction", ""))
                confidence_raw = item.get("confidence_score")
                confidence = (
                    float(confidence_raw) if isinstance(confidence_raw, int | float) else None
                )
                item["body"] = _format_notification_body(
                    dataset_id=dataset_id,
                    previous=previous,
                    current=current,
                    confidence=confidence,
                )
                normalized_items.append(item)
            payload = {**payload, "items": normalized_items}

        return NotificationListResponse.model_validate(payload)

    def get_unread_summary(self, *, user_id: str) -> NotificationSummaryResponse:
        """Return unread summary for shell badge and recent checks."""

        payload = self.repository.get_unread_summary(user_id=user_id)
        return NotificationSummaryResponse.model_validate(payload)

    def mark_notification_read(
        self,
        *,
        user_id: str,
        notification_id: str,
    ) -> MarkReadResponse:
        """Mark one notification read and return updated unread summary count."""

        updated = self.repository.mark_notification_read(
            user_id=user_id,
            notification_id=notification_id,
        )
        if not updated:
            raise ContractQueryError("notification_not_found")

        summary = self.repository.get_unread_summary(user_id=user_id)
        unread_count_raw = summary.get("unread_count")
        unread_count = int(unread_count_raw) if isinstance(unread_count_raw, int) else 0
        return MarkReadResponse(
            notification_id=notification_id,
            updated=True,
            unread_count=unread_count,
        )

    def mark_notification_unread(
        self,
        *,
        user_id: str,
        notification_id: str,
    ) -> MarkUnreadResponse:
        """Mark one notification unread and return updated unread summary count."""

        updated = self.repository.mark_notification_unread(
            user_id=user_id,
            notification_id=notification_id,
        )
        if not updated:
            raise ContractQueryError("notification_not_found")

        summary = self.repository.get_unread_summary(user_id=user_id)
        unread_count_raw = summary.get("unread_count")
        unread_count = int(unread_count_raw) if isinstance(unread_count_raw, int) else 0
        return MarkUnreadResponse(
            notification_id=notification_id,
            updated=True,
            unread_count=unread_count,
        )

    def mark_all_notifications_read(self, *, user_id: str) -> MarkAllReadResponse:
        """Mark all unread notifications read for one user."""

        updated_count = self.repository.mark_all_notifications_read(user_id=user_id)
        return MarkAllReadResponse(updated_count=updated_count, unread_count=0)

    def list_subscriptions(self, *, user_id: str) -> SubscriptionListResponse:
        """Return active subscriptions for one user."""

        payload = {"items": self.repository.list_active_subscriptions(user_id=user_id)}
        return SubscriptionListResponse.model_validate(payload)

    def create_subscription(
        self,
        *,
        user_id: str,
        dataset_id: str,
    ) -> SubscriptionResponse:
        """Create/reactivate one subscription and return result payload."""

        normalized_dataset_id = dataset_id.strip()
        if normalized_dataset_id == "":
            raise ContractQueryError("dataset_id must be provided")

        payload = self.repository.create_or_reactivate_subscription(
            user_id=user_id,
            dataset_id=normalized_dataset_id,
        )
        if payload is None:
            raise ContractQueryError("dataset_not_found")
        return SubscriptionResponse.model_validate(payload)

    def delete_subscription(
        self,
        *,
        user_id: str,
        dataset_id: str,
    ) -> DeleteSubscriptionResponse:
        """Remove one active subscription and return removal status."""

        normalized_dataset_id = dataset_id.strip()
        if normalized_dataset_id == "":
            raise ContractQueryError("dataset_id must be provided")

        removed = self.repository.remove_active_subscription(
            user_id=user_id,
            dataset_id=normalized_dataset_id,
        )
        return DeleteSubscriptionResponse(
            dataset_id=normalized_dataset_id,
            removed=removed,
        )

    @staticmethod
    def generated_at_iso() -> str:
        """Return UTC timestamp text for response metadata fallbacks."""

        return datetime.now(tz=UTC).isoformat()
