"""US3 contract tests for confidence-threshold notification copy formatting."""

# ruff: noqa: D103

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast
from uuid import uuid4

from src.query.trend_notification_service import (
    TrendNotificationService,
    TrendNotificationServiceRepository,
)


class _RepoDouble:
    def __init__(self) -> None:
        now = datetime.now(tz=UTC).isoformat()
        self.payload: dict[str, object] = {
            "items": [
                {
                    "notification_id": str(uuid4()),
                    "event_id": str(uuid4()),
                    "dataset_id": "PRICE.US.CPI",
                    "title": "Trend reversal detected",
                    "body": "PRICE.US.CPI: up to down",
                    "previous_direction": "up",
                    "current_direction": "down",
                    "confidence_score": 0.70,
                    "effective_observed_on": "2026-01-01",
                    "destination_path": "/datasets/PRICE.US.CPI",
                    "unread": True,
                    "read_at": None,
                    "delivered_at": now,
                    "channel": "in_app",
                    "delivery_status": "delivered",
                    "processing_context": "incremental",
                    "visibility_classification": "user_visible",
                }
            ],
            "pagination": {"page_size": 25, "has_more": False, "next_cursor": None},
        }

    def list_notifications(
        self,
        *,
        user_id: str,
        page_size: int,
        cursor: str | None,
        unread_only: bool,
    ) -> dict[str, object]:
        del user_id, page_size, cursor, unread_only
        return dict(self.payload)

    def get_unread_summary(self, *, user_id: str) -> dict[str, object]:
        del user_id
        return {
            "unread_count": 1,
            "last_notification_at": None,
            "generated_at": datetime.now(tz=UTC).isoformat(),
        }

    def mark_notification_read(self, *, user_id: str, notification_id: str) -> bool:
        del user_id, notification_id
        return True

    def mark_notification_unread(self, *, user_id: str, notification_id: str) -> bool:
        del user_id, notification_id
        return True

    def mark_all_notifications_read(self, *, user_id: str) -> int:
        del user_id
        return 0

    def list_active_subscriptions(self, *, user_id: str) -> list[dict[str, object]]:
        del user_id
        return []

    def create_or_reactivate_subscription(
        self,
        *,
        user_id: str,
        dataset_id: str,
    ) -> dict[str, object] | None:
        del user_id, dataset_id
        return None

    def remove_active_subscription(self, *, user_id: str, dataset_id: str) -> bool:
        del user_id, dataset_id
        return False


def test_notification_body_includes_confidence_when_threshold_met() -> None:
    repo = _RepoDouble()
    service = TrendNotificationService(repository=cast(TrendNotificationServiceRepository, repo))

    response = service.list_notifications(
        user_id=str(uuid4()),
        page_size=25,
        cursor=None,
        unread_only=False,
    )

    assert response.items[0].body.endswith("(confidence 0.70)")


def test_notification_body_omits_confidence_when_below_threshold() -> None:
    repo = _RepoDouble()
    items = cast(list[dict[str, object]], repo.payload["items"])
    items[0]["confidence_score"] = 0.69
    service = TrendNotificationService(repository=cast(TrendNotificationServiceRepository, repo))

    response = service.list_notifications(
        user_id=str(uuid4()),
        page_size=25,
        cursor=None,
        unread_only=False,
    )

    assert response.items[0].body == "PRICE.US.CPI: up to down"
