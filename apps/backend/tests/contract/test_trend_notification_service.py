"""Unit coverage for trend notification backend service workflows."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest

from src.contract.errors import ContractQueryError
from src.query.trend_notification_service import TrendNotificationService


class _RepoDouble:
    def __init__(self) -> None:
        now = datetime.now(tz=UTC).isoformat()
        notification_id = str(uuid4())
        event_id = str(uuid4())
        self.list_payload = {
            "items": [
                {
                    "notification_id": notification_id,
                    "event_id": event_id,
                    "dataset_id": "PRICE.US.CPI",
                    "title": "Trend reversal detected",
                    "body": "PRICE.US.CPI: up to down",
                    "previous_direction": "up",
                    "current_direction": "down",
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
            "pagination": {
                "page_size": 25,
                "has_more": False,
                "next_cursor": None,
            },
        }
        self.summary_payload = {
            "unread_count": 1,
            "last_notification_at": now,
            "generated_at": now,
        }
        self.subscription_rows = [
            {
                "dataset_id": "PRICE.US.CPI",
                "subscribed_at": now,
                "unsubscribed_at": None,
            }
        ]
        self.mark_read_result = True
        self.mark_unread_result = True
        self.mark_all_result = 1
        self.create_subscription_result: dict[str, object] | None = {
            "dataset_id": "PRICE.US.CPI",
            "subscribed_at": now,
            "created": True,
        }
        self.remove_subscription_result = True

    def list_notifications(
        self,
        *,
        user_id: str,
        page_size: int,
        cursor: str | None,
        unread_only: bool,
    ) -> dict[str, object]:
        del user_id, page_size, cursor, unread_only
        return dict(self.list_payload)

    def get_unread_summary(self, *, user_id: str) -> dict[str, object]:
        del user_id
        return dict(self.summary_payload)

    def mark_notification_read(self, *, user_id: str, notification_id: str) -> bool:
        del user_id, notification_id
        return self.mark_read_result

    def mark_notification_unread(self, *, user_id: str, notification_id: str) -> bool:
        del user_id, notification_id
        return self.mark_unread_result

    def mark_all_notifications_read(self, *, user_id: str) -> int:
        del user_id
        return self.mark_all_result

    def list_active_subscriptions(self, *, user_id: str) -> list[dict[str, object]]:
        del user_id
        return list(self.subscription_rows)

    def create_or_reactivate_subscription(
        self,
        *,
        user_id: str,
        dataset_id: str,
    ) -> dict[str, object] | None:
        del user_id, dataset_id
        return self.create_subscription_result

    def remove_active_subscription(self, *, user_id: str, dataset_id: str) -> bool:
        del user_id, dataset_id
        return self.remove_subscription_result


def _service_and_repo() -> tuple[TrendNotificationService, _RepoDouble]:
    repo = _RepoDouble()
    service = TrendNotificationService(repository=repo)
    return service, repo


def test_service_list_summary_and_mutation_paths() -> None:
    """Service should return valid list/summary and read-state mutation payloads."""

    service, repo = _service_and_repo()

    listing = service.list_notifications(
        user_id=str(uuid4()),
        page_size=25,
        cursor=None,
        unread_only=False,
    )
    summary = service.get_unread_summary(user_id=str(uuid4()))
    mark_read = service.mark_notification_read(
        user_id=str(uuid4()),
        notification_id=str(uuid4()),
    )
    mark_unread = service.mark_notification_unread(
        user_id=str(uuid4()),
        notification_id=str(uuid4()),
    )
    mark_all = service.mark_all_notifications_read(user_id=str(uuid4()))

    assert len(listing.items) == 1
    assert summary.unread_count == 1
    assert mark_read.updated is True
    assert mark_unread.updated is True
    assert mark_all.updated_count == repo.mark_all_result


def test_service_supports_subscription_lifecycle_paths() -> None:
    """Service should list/create/delete user-owned subscriptions."""

    service, _repo = _service_and_repo()

    listed = service.list_subscriptions(user_id=str(uuid4()))
    created = service.create_subscription(user_id=str(uuid4()), dataset_id="PRICE.US.CPI")
    removed = service.delete_subscription(user_id=str(uuid4()), dataset_id="PRICE.US.CPI")

    assert listed.items[0].dataset_id == "PRICE.US.CPI"
    assert created.dataset_id == "PRICE.US.CPI"
    assert removed.removed is True


def test_service_rejects_out_of_contract_inputs_and_missing_rows() -> None:
    """Service should raise contract errors for invalid input and missing rows."""

    service, repo = _service_and_repo()

    with pytest.raises(ContractQueryError, match="page_size must be between 1 and 100"):
        service.list_notifications(
            user_id=str(uuid4()),
            page_size=0,
            cursor=None,
            unread_only=False,
        )

    repo.mark_read_result = False
    with pytest.raises(ContractQueryError, match="notification_not_found"):
        service.mark_notification_read(
            user_id=str(uuid4()),
            notification_id=str(uuid4()),
        )

    repo.mark_unread_result = False
    with pytest.raises(ContractQueryError, match="notification_not_found"):
        service.mark_notification_unread(
            user_id=str(uuid4()),
            notification_id=str(uuid4()),
        )

    repo.create_subscription_result = None
    with pytest.raises(ContractQueryError, match="dataset_not_found"):
        service.create_subscription(user_id=str(uuid4()), dataset_id="UNKNOWN.DATASET")

    with pytest.raises(ContractQueryError, match="dataset_id must be provided"):
        service.create_subscription(user_id=str(uuid4()), dataset_id=" ")

    with pytest.raises(ContractQueryError, match="dataset_id must be provided"):
        service.delete_subscription(user_id=str(uuid4()), dataset_id="")


def test_service_list_ordering_and_unread_summary_fields_pass_through() -> None:
    """Service should preserve repository ordering and summary field values."""

    service, repo = _service_and_repo()
    now = datetime.now(tz=UTC).isoformat()
    repo.list_payload = {
        "items": [
            {
                **repo.list_payload["items"][0],
                "notification_id": str(uuid4()),
                "delivered_at": now,
            },
            {
                **repo.list_payload["items"][0],
                "notification_id": str(uuid4()),
                "delivered_at": "2025-01-01T00:00:00+00:00",
            },
        ],
        "pagination": {
            "page_size": 2,
            "has_more": True,
            "next_cursor": "2025-01-01T00:00:00+00:00|cursor",
        },
    }
    repo.summary_payload = {
        "unread_count": 5,
        "last_notification_at": now,
        "generated_at": now,
    }

    listing = service.list_notifications(
        user_id=str(uuid4()),
        page_size=2,
        cursor=None,
        unread_only=False,
    )
    summary = service.get_unread_summary(user_id=str(uuid4()))

    assert listing.items[0].delivered_at == now
    assert listing.pagination.has_more is True
    assert listing.pagination.next_cursor is not None
    assert summary.unread_count == 5
    assert summary.last_notification_at == now


def test_service_new_user_default_empty_subscriptions() -> None:
    """New users with no subscriptions should receive contract-valid empty payload."""

    service, repo = _service_and_repo()
    repo.subscription_rows = []

    listed = service.list_subscriptions(user_id=str(uuid4()))

    assert listed.items == []
