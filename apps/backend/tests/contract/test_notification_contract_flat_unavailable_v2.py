"""US3 contract tests for flat/unavailable non-directional notification semantics."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from src.query.trend_notification_service import TrendNotificationService


class _RepoDouble:
    def __init__(self) -> None:
        now = datetime.now(tz=UTC).isoformat()
        self.payload = {
            "items": [
                {
                    "notification_id": str(uuid4()),
                    "event_id": str(uuid4()),
                    "dataset_id": "PRICE.US.CPI",
                    "title": "Trend reversal detected",
                    "body": "placeholder",
                    "previous_direction": "up",
                    "current_direction": "down",
                    "confidence_score": None,
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
        return self.payload


def test_notification_contract_remains_directional_without_flat_or_unavailable_states() -> None:
    repo = _RepoDouble()
    service = TrendNotificationService(repository=repo)

    listing = service.list_notifications(
        user_id=str(uuid4()),
        page_size=25,
        cursor=None,
        unread_only=False,
    )

    assert listing.items[0].previous_direction in {"up", "down"}
    assert listing.items[0].current_direction in {"up", "down"}
    assert listing.items[0].body == "PRICE.US.CPI: up to down"
