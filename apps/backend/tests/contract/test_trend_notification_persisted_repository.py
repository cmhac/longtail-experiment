"""Unit coverage for persisted notification repository adapter methods."""

# ruff: noqa: D103

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import cast
from uuid import UUID, uuid4

from sqlalchemy import Engine

from src.query.trend_notification_persisted_repository import (
    PersistedTrendNotificationRepository,
)

_EXPECTED_UNREAD_COUNT = 2
_EXPECTED_MARK_ALL_COUNT = 3


class _Result:
    def __init__(
        self,
        *,
        mappings_first: dict[str, object] | None = None,
        mappings_all: list[dict[str, object]] | None = None,
        mappings_one: dict[str, object] | None = None,
        scalar_one_or_none: object = None,
        rowcount: int = 0,
    ) -> None:
        self._mappings_first = mappings_first
        self._mappings_all = mappings_all or []
        self._mappings_one = mappings_one
        self._scalar_one_or_none = scalar_one_or_none
        self.rowcount = rowcount

    def mappings(self) -> _Result:
        return self

    def first(self) -> dict[str, object] | None:
        return self._mappings_first

    def all(self) -> list[dict[str, object]]:
        return self._mappings_all

    def one(self) -> dict[str, object]:
        if self._mappings_one is None:
            raise AssertionError("expected mappings_one")
        return self._mappings_one

    def scalar_one_or_none(self) -> object:
        return self._scalar_one_or_none


class _ConnectionDouble:
    def __init__(self) -> None:
        self.executed: list[tuple[str, dict[str, object] | None]] = []
        now = datetime.now(tz=UTC)

        self.series_id: UUID | None = uuid4()
        self.notification_rows: list[dict[str, object]] = [
            {
                "notification_id": uuid4(),
                "event_id": uuid4(),
                "dataset_id": "PRICE.US.CPI",
                "title": "Trend reversal detected",
                "body": "PRICE.US.CPI: up to down",
                "destination_path": "/datasets/PRICE.US.CPI",
                "unread": True,
                "read_at": None,
                "delivered_at": now,
                "channel": "in_app",
                "delivery_status": "delivered",
                "previous_direction": "up",
                "current_direction": "down",
                "confidence_score": 0.74,
                "effective_observed_on": "2026-01-01",
                "processing_context": "incremental",
                "visibility_classification": "user_visible",
            }
        ]
        self.unread_summary_row: dict[str, object] = {
            "unread_count": 2,
            "last_notification_at": now,
        }
        self.mark_read_id: object = uuid4()
        self.mark_unread_id: object = uuid4()
        self.mark_all_rowcount = 3
        self.subscription_rows: list[dict[str, object]] = [
            {
                "dataset_id": "PRICE.US.CPI",
                "subscribed_at": now,
                "unsubscribed_at": None,
            }
        ]
        self.existing_active_subscription: dict[str, object] | None = None
        self.existing_inactive_subscription: dict[str, object] | None = None
        self.remove_rowcount = 1

    def execute(self, statement: object, params: dict[str, object] | None = None) -> _Result:  # noqa: PLR0911
        sql = str(statement)
        self.executed.append((sql, params))

        if "FROM data_series" in sql and "WHERE series_key = :series_key" in sql:
            return _Result(scalar_one_or_none=self.series_id)

        if "FROM user_trend_notifications utn" in sql:
            return _Result(mappings_all=self.notification_rows)

        if "MAX(delivered_at) AS last_notification_at" in sql:
            return _Result(mappings_one=self.unread_summary_row)

        if (
            "SET\n                        unread_state = 'read'" in sql
            and "WHERE id = :notification_id" in sql
        ):
            return _Result(scalar_one_or_none=self.mark_read_id)

        if "SET\n                        unread_state = 'unread'" in sql:
            return _Result(scalar_one_or_none=self.mark_unread_id)

        if "WHERE user_id = :user_id" in sql and "unread_state = 'unread'" in sql:
            return _Result(rowcount=self.mark_all_rowcount)

        if "SELECT\n                            ds.series_key AS dataset_id" in sql:
            return _Result(mappings_all=self.subscription_rows)

        if "FROM user_dataset_subscriptions" in sql and "unsubscribed_at IS NULL" in sql:
            return _Result(mappings_first=self.existing_active_subscription)

        if "FROM user_dataset_subscriptions" in sql and "ORDER BY subscribed_at DESC" in sql:
            return _Result(mappings_first=self.existing_inactive_subscription)

        if (
            "UPDATE user_dataset_subscriptions" in sql
            and "unsubscribed_at = :unsubscribed_at" in sql
        ):
            return _Result(rowcount=self.remove_rowcount)

        return _Result()


class _EngineDouble:
    def __init__(self, connection: _ConnectionDouble) -> None:
        self._connection = connection

    @contextmanager
    def begin(self) -> Iterator[_ConnectionDouble]:
        yield self._connection


def test_notification_persisted_repository_paths() -> None:
    connection = _ConnectionDouble()
    repository = PersistedTrendNotificationRepository(
        engine=cast(Engine, _EngineDouble(connection))
    )

    listed = repository.list_notifications(
        user_id=str(uuid4()),
        page_size=1,
        cursor=None,
        unread_only=False,
    )
    summary = repository.get_unread_summary(user_id=str(uuid4()))
    mark_read = repository.mark_notification_read(
        user_id=str(uuid4()),
        notification_id=str(uuid4()),
    )
    mark_unread = repository.mark_notification_unread(
        user_id=str(uuid4()),
        notification_id=str(uuid4()),
    )
    mark_all = repository.mark_all_notifications_read(user_id=str(uuid4()))
    subscriptions = repository.list_active_subscriptions(user_id=str(uuid4()))
    created = repository.create_or_reactivate_subscription(
        user_id=str(uuid4()),
        dataset_id="PRICE.US.CPI",
    )
    removed = repository.remove_active_subscription(
        user_id=str(uuid4()),
        dataset_id="PRICE.US.CPI",
    )

    assert len(cast(list[dict[str, object]], listed["items"])) == 1
    assert cast(dict[str, object], listed["pagination"])["has_more"] is False
    assert summary["unread_count"] == _EXPECTED_UNREAD_COUNT
    assert mark_read is True
    assert mark_unread is True
    assert mark_all == _EXPECTED_MARK_ALL_COUNT
    assert subscriptions[0]["dataset_id"] == "PRICE.US.CPI"
    assert created is not None
    assert created["created"] is True
    assert removed is True


def test_notification_persisted_repository_edge_paths() -> None:
    connection = _ConnectionDouble()
    connection.notification_rows = [
        {
            **connection.notification_rows[0],
            "notification_id": uuid4(),
            "read_at": datetime.now(tz=UTC),
        },
        {
            **connection.notification_rows[0],
            "notification_id": uuid4(),
        },
    ]
    connection.mark_read_id = None
    connection.mark_unread_id = None
    connection.mark_all_rowcount = 0
    connection.series_id = None
    connection.remove_rowcount = 0
    connection.existing_active_subscription = {
        "id": uuid4(),
        "subscribed_at": datetime.now(tz=UTC),
    }
    repository = PersistedTrendNotificationRepository(
        engine=cast(Engine, _EngineDouble(connection))
    )

    listed = repository.list_notifications(
        user_id=str(uuid4()),
        page_size=1,
        cursor=None,
        unread_only=False,
    )
    mark_read = repository.mark_notification_read(
        user_id=str(uuid4()),
        notification_id=str(uuid4()),
    )
    mark_unread = repository.mark_notification_unread(
        user_id=str(uuid4()),
        notification_id=str(uuid4()),
    )
    mark_all = repository.mark_all_notifications_read(user_id=str(uuid4()))
    created = repository.create_or_reactivate_subscription(
        user_id=str(uuid4()),
        dataset_id="MISSING.DATASET",
    )
    removed = repository.remove_active_subscription(
        user_id=str(uuid4()),
        dataset_id="MISSING.DATASET",
    )

    assert cast(dict[str, object], listed["pagination"])["has_more"] is True
    assert cast(dict[str, object], listed["pagination"])["next_cursor"] is not None
    assert mark_read is False
    assert mark_unread is False
    assert mark_all == 0
    assert created is None
    assert removed is False
