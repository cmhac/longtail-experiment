"""Contract schema coverage for trend notification API models."""

from __future__ import annotations

from src.contract.query.trend_notification_query import (
    CreateSubscriptionRequest,
    DeleteSubscriptionResponse,
    MarkAllReadResponse,
    MarkReadResponse,
    MarkUnreadResponse,
    NotificationListResponse,
    NotificationSummaryResponse,
    SubscriptionListResponse,
    SubscriptionResponse,
    notification_not_found_error,
    notification_unauthorized_error,
    notification_validation_error,
)

_EXPECTED_UNREAD_COUNT = 2


def test_notification_schema_models_validate_expected_shapes() -> None:
    """Notification request/response contracts should validate expected payloads."""
    listing = NotificationListResponse.model_validate(
        {
            "items": [
                {
                    "notification_id": "00000000-0000-0000-0000-000000000001",
                    "event_id": "00000000-0000-0000-0000-000000000002",
                    "dataset_id": "PRICE.US.CPI",
                    "title": "Trend reversal detected",
                    "body": "PRICE.US.CPI: up to down",
                    "previous_direction": "up",
                    "current_direction": "down",
                    "confidence_score": 0.74,
                    "effective_observed_on": "2026-01-01",
                    "destination_path": "/datasets/PRICE.US.CPI",
                    "unread": True,
                    "read_at": None,
                    "delivered_at": "2026-01-02T00:00:00+00:00",
                    "channel": "in_app",
                    "delivery_status": "delivered",
                    "processing_context": "incremental",
                    "visibility_classification": "user_visible",
                }
            ],
            "pagination": {
                "page_size": 25,
                "has_more": False,
                "next_cursor": None,
            },
        }
    )
    summary = NotificationSummaryResponse.model_validate(
        {
            "unread_count": 2,
            "last_notification_at": "2026-01-02T00:00:00+00:00",
            "generated_at": "2026-01-02T00:00:01+00:00",
        }
    )
    mark_read = MarkReadResponse.model_validate(
        {
            "notification_id": "00000000-0000-0000-0000-000000000001",
            "updated": True,
            "unread_count": 1,
        }
    )
    mark_unread = MarkUnreadResponse.model_validate(
        {
            "notification_id": "00000000-0000-0000-0000-000000000001",
            "updated": True,
            "unread_count": 2,
        }
    )
    mark_all = MarkAllReadResponse.model_validate(
        {
            "updated_count": 2,
            "unread_count": 0,
        }
    )
    request = CreateSubscriptionRequest.model_validate({"dataset_id": "PRICE.US.CPI"})
    subscription = SubscriptionResponse.model_validate(
        {
            "dataset_id": "PRICE.US.CPI",
            "subscribed_at": "2026-01-02T00:00:00+00:00",
            "created": True,
        }
    )
    subscriptions = SubscriptionListResponse.model_validate(
        {
            "items": [
                {
                    "dataset_id": "PRICE.US.CPI",
                    "subscribed_at": "2026-01-02T00:00:00+00:00",
                    "unsubscribed_at": None,
                }
            ]
        }
    )
    deleted = DeleteSubscriptionResponse.model_validate(
        {
            "dataset_id": "PRICE.US.CPI",
            "removed": True,
        }
    )

    assert listing.items[0].dataset_id == "PRICE.US.CPI"
    assert summary.unread_count == _EXPECTED_UNREAD_COUNT
    assert mark_read.updated is True
    assert mark_unread.updated is True
    assert mark_all.updated_count == _EXPECTED_UNREAD_COUNT
    assert request.dataset_id == "PRICE.US.CPI"
    assert subscription.created is True
    assert subscriptions.items[0].dataset_id == "PRICE.US.CPI"
    assert deleted.removed is True


def test_notification_error_envelopes_are_standardized() -> None:
    """Notification error envelopes should expose stable error-code fields."""
    unauthorized = notification_unauthorized_error().model_dump()
    not_found = notification_not_found_error("Missing").model_dump()
    invalid = notification_validation_error("bad request").model_dump()

    assert unauthorized["error"]["code"] == "unauthorized"
    assert not_found["error"]["code"] == "notification_not_found"
    assert invalid["error"]["code"] == "invalid_request"
