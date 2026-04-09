"""Contract models and error envelopes for trend notification workflows."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class NotificationApiErrorPayload(BaseModel):
    """Error payload returned by trend notification endpoints."""

    code: str = Field(min_length=1)
    message: str = Field(min_length=1)


class NotificationApiErrorEnvelope(BaseModel):
    """Standardized error envelope for trend notification workflows."""

    error: NotificationApiErrorPayload


class NotificationListItem(BaseModel):
    """Serialized one in-app notification list row."""

    notification_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    dataset_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)
    previous_direction: Literal["up", "down"]
    current_direction: Literal["up", "down"]
    confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    effective_observed_on: str = Field(min_length=1)
    destination_path: str = Field(min_length=1)
    unread: bool
    read_at: str | None = None
    delivered_at: str = Field(min_length=1)
    channel: Literal["in_app"]
    delivery_status: Literal["queued", "delivered", "failed", "suppressed"]
    processing_context: Literal["incremental", "historical_reprocessing"]
    visibility_classification: Literal["user_visible", "audit_only"]


class NotificationPaginationInfo(BaseModel):
    """Stable cursor pagination metadata for notification lists."""

    page_size: int = Field(ge=1, le=100)
    has_more: bool
    next_cursor: str | None = None


class NotificationListResponse(BaseModel):
    """Paginated newest-first trend notification list response."""

    items: list[NotificationListItem]
    pagination: NotificationPaginationInfo


class NotificationSummaryResponse(BaseModel):
    """Unread summary response for shell badge and quick checks."""

    unread_count: int = Field(ge=0)
    last_notification_at: str | None = None
    generated_at: str = Field(min_length=1)


class MarkReadResponse(BaseModel):
    """One-item mark-read response."""

    notification_id: str = Field(min_length=1)
    updated: bool
    unread_count: int = Field(ge=0)


class MarkUnreadResponse(BaseModel):
    """One-item mark-unread response."""

    notification_id: str = Field(min_length=1)
    updated: bool
    unread_count: int = Field(ge=0)


class MarkAllReadResponse(BaseModel):
    """Bulk mark-all-read response."""

    updated_count: int = Field(ge=0)
    unread_count: int = Field(ge=0)


class DatasetSubscriptionItem(BaseModel):
    """One active dataset subscription summary row."""

    dataset_id: str = Field(min_length=1)
    subscribed_at: str = Field(min_length=1)
    unsubscribed_at: str | None = None


class SubscriptionListResponse(BaseModel):
    """List of active subscriptions for authenticated user."""

    items: list[DatasetSubscriptionItem]


class CreateSubscriptionRequest(BaseModel):
    """Input payload for creating or reactivating one subscription."""

    dataset_id: str = Field(min_length=1)


class SubscriptionResponse(BaseModel):
    """Result payload for create/reactivate subscription action."""

    dataset_id: str = Field(min_length=1)
    subscribed_at: str = Field(min_length=1)
    created: bool


class DeleteSubscriptionResponse(BaseModel):
    """Result payload for removing one active subscription."""

    dataset_id: str = Field(min_length=1)
    removed: bool


def notification_error(
    code: str,
    message: str,
) -> NotificationApiErrorEnvelope:
    """Create a standard notification error envelope."""
    return NotificationApiErrorEnvelope(
        error=NotificationApiErrorPayload(code=code, message=message)
    )


def notification_unauthorized_error(
    message: str = "Authentication required",
) -> NotificationApiErrorEnvelope:
    """Create a standard authentication error envelope."""
    return notification_error("unauthorized", message)


def notification_not_found_error(
    message: str,
) -> NotificationApiErrorEnvelope:
    """Create a standard notification not-found error envelope."""
    return notification_error("notification_not_found", message)


def notification_validation_error(
    message: str,
) -> NotificationApiErrorEnvelope:
    """Create a standard invalid-request error envelope."""
    return notification_error("invalid_request", message)
