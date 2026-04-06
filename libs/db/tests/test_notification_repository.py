"""Unit tests for postgres trend notification repository behavior."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from datetime import UTC, date, datetime
import sys
from pathlib import Path
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from sqlalchemy import Engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from db.repositories.notification_repository import PostgresNotificationRepository


class _Result:
    def __init__(
        self,
        *,
        mappings_first: Mapping[str, object] | None = None,
        mappings_all: Sequence[Mapping[str, object]] | None = None,
        mappings_one: Mapping[str, object] | None = None,
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
        if self._mappings_first is None:
            return None
        return dict(self._mappings_first)

    def all(self) -> list[dict[str, object]]:
        return [dict(row) for row in self._mappings_all]

    def one(self) -> dict[str, object]:
        if self._mappings_one is None:
            raise AssertionError("expected mappings_one in test double")
        return dict(self._mappings_one)

    def scalar_one_or_none(self) -> object:
        return self._scalar_one_or_none


class _ConnectionDouble:
    def __init__(self) -> None:
        now = datetime.now(tz=UTC)
        self.executed: list[tuple[str, dict[str, object] | None]] = []

        self.series_id: UUID | None = uuid4()
        self.previous_direction: str | None = "up"

        self.inserted_event_id: UUID | None = uuid4()
        self.existing_event_id: UUID | None = uuid4()

        self.event_row: dict[str, object] | None = {
            "id": uuid4(),
            "data_series_id": uuid4(),
            "dataset_id": "PRICE.US.CPI",
            "previous_direction": "up",
            "current_direction": "down",
            "effective_observed_on": date(2026, 1, 1),
            "processing_context": "incremental",
            "visibility_classification": "user_visible",
            "emitted_at": now,
        }
        self.eligible_rows: list[dict[str, object]] = [{"user_id": uuid4()}]
        self.fanout_insert_rowcount: int = 1

        notification_id = uuid4()
        event_id = uuid4()
        self.notification_rows: list[dict[str, object]] = [
            {
                "notification_id": notification_id,
                "event_id": event_id,
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
                "effective_observed_on": date(2026, 1, 1),
                "processing_context": "incremental",
                "visibility_classification": "user_visible",
            }
        ]
        self.unread_summary_row: dict[str, object] = {
            "unread_count": 4,
            "last_notification_at": now,
        }

        self.mark_read_id: object = uuid4()
        self.mark_unread_id: object = uuid4()
        self.mark_all_rowcount: int = 2

        self.subscription_rows: list[dict[str, object]] = [
            {
                "dataset_id": "PRICE.US.CPI",
                "subscribed_at": now,
                "unsubscribed_at": None,
            }
        ]
        self.existing_active_subscription: dict[str, object] | None = None
        self.existing_inactive_subscription: dict[str, object] | None = None
        self.remove_rowcount: int = 1
        self.retention_delete_rowcount: int = 0

    def execute(
        self, statement: object, params: dict[str, object] | None = None
    ) -> _Result:
        sql = str(statement)
        self.executed.append((sql, params))

        if "INSERT INTO trend_change_events" in sql:
            inserted = (
                {"id": self.inserted_event_id}
                if self.inserted_event_id is not None
                else None
            )
            return _Result(mappings_first=inserted)

        if "FROM data_series" in sql and "WHERE series_key = :series_key" in sql:
            return _Result(scalar_one_or_none=self.series_id)

        if "FROM trend_canonical_descriptors" in sql:
            return _Result(scalar_one_or_none=self.previous_direction)

        if (
            "FROM trend_change_events" in sql
            and "idempotency_fingerprint" in sql
            and "SELECT id" in sql
        ):
            existing = (
                {"id": self.existing_event_id}
                if self.existing_event_id is not None
                else None
            )
            return _Result(mappings_first=existing)

        if "FROM trend_change_events tce" in sql and "WHERE tce.id = :event_id" in sql:
            return _Result(mappings_first=self.event_row)

        if "FROM user_dataset_subscriptions uds" in sql and "SELECT uds.user_id" in sql:
            return _Result(mappings_all=self.eligible_rows)

        if "INSERT INTO user_trend_notifications" in sql and "ON CONFLICT" in sql:
            return _Result(rowcount=self.fanout_insert_rowcount)

        if "FROM user_trend_notifications utn" in sql:
            return _Result(mappings_all=self.notification_rows)

        if "MAX(delivered_at) AS last_notification_at" in sql:
            return _Result(mappings_one=self.unread_summary_row)

        if (
            "UPDATE user_trend_notifications" in sql
            and "SET\n                        unread_state = 'read'" in sql
            and "WHERE id = :notification_id" in sql
        ):
            return _Result(scalar_one_or_none=self.mark_read_id)

        if (
            "UPDATE user_trend_notifications" in sql
            and "SET\n                        unread_state = 'unread'" in sql
        ):
            return _Result(scalar_one_or_none=self.mark_unread_id)

        if (
            "UPDATE user_trend_notifications" in sql
            and "WHERE user_id = :user_id" in sql
        ):
            return _Result(rowcount=self.mark_all_rowcount)

        if "SELECT\n                            ds.series_key AS dataset_id" in sql:
            return _Result(mappings_all=self.subscription_rows)

        if (
            "FROM user_dataset_subscriptions" in sql
            and "unsubscribed_at IS NULL" in sql
        ):
            return _Result(mappings_first=self.existing_active_subscription)

        if (
            "FROM user_dataset_subscriptions" in sql
            and "ORDER BY subscribed_at DESC" in sql
        ):
            return _Result(mappings_first=self.existing_inactive_subscription)

        if (
            "UPDATE user_dataset_subscriptions" in sql
            and "unsubscribed_at = :unsubscribed_at" in sql
        ):
            return _Result(rowcount=self.remove_rowcount)

        if "DELETE FROM user_trend_notifications" in sql:
            return _Result(rowcount=self.retention_delete_rowcount)

        return _Result()


class _EngineDouble:
    def __init__(self, connection: _ConnectionDouble) -> None:
        self._connection = connection

    @contextmanager
    def begin(self) -> Iterator[_ConnectionDouble]:
        yield self._connection


def _repo(connection: _ConnectionDouble) -> PostgresNotificationRepository:
    return PostgresNotificationRepository(
        engine=cast(Engine, _EngineDouble(connection))
    )


def test_notification_repository_covers_core_paths() -> None:
    connection = _ConnectionDouble()
    repository = _repo(connection)

    previous = repository.get_previous_canonical_direction(
        series_key="PRICE.US.CPI",
        observed_on=date(2026, 1, 2),
    )
    append_result = repository.append_trend_change_event(
        {
            "series_key": "PRICE.US.CPI",
            "previous_direction": "up",
            "current_direction": "down",
            "effective_observed_on": date(2026, 1, 2),
            "processing_context": "incremental",
            "visibility_classification": "user_visible",
            "idempotency_fingerprint": "PRICE.US.CPI|2026-01-02|up|down|incremental",
            "emitted_at": datetime.now(tz=UTC),
        }
    )
    assert connection.event_row is not None
    fanout_count = repository.fan_out_notifications_for_event(
        event_id=str(connection.event_row["id"])
    )
    listed = repository.list_notifications(
        user_id=str(uuid4()),
        page_size=10,
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
    mark_all_count = repository.mark_all_notifications_read(user_id=str(uuid4()))
    subscriptions = repository.list_active_subscriptions(user_id=str(uuid4()))
    created = repository.create_or_reactivate_subscription(
        user_id=str(uuid4()),
        dataset_id="PRICE.US.CPI",
        now=datetime.now(tz=UTC),
    )
    removed = repository.remove_active_subscription(
        user_id=str(uuid4()),
        dataset_id="PRICE.US.CPI",
        now=datetime.now(tz=UTC),
    )

    assert previous == "up"
    assert append_result["inserted"] is True
    assert fanout_count == 1
    assert len(cast(list[dict[str, Any]], listed["items"])) == 1
    assert cast(dict[str, Any], listed["pagination"])["has_more"] is False
    assert summary["unread_count"] == 4
    assert mark_read is True
    assert mark_unread is True
    assert mark_all_count == 2
    assert subscriptions[0]["dataset_id"] == "PRICE.US.CPI"
    assert created is not None
    assert created["created"] is True
    assert removed is True


def test_notification_repository_handles_idempotent_and_edge_paths() -> None:
    connection = _ConnectionDouble()
    connection.previous_direction = "sideways"
    connection.inserted_event_id = None
    connection.existing_event_id = uuid4()
    connection.event_row = {
        "id": uuid4(),
        "data_series_id": uuid4(),
        "dataset_id": "PRICE.US.CPI",
        "previous_direction": "up",
        "current_direction": "down",
        "effective_observed_on": date(2026, 1, 1),
        "processing_context": "historical_reprocessing",
        "visibility_classification": "audit_only",
        "emitted_at": datetime.now(tz=UTC),
    }
    connection.notification_rows = [
        {
            **connection.notification_rows[0],
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
    repository = _repo(connection)

    previous = repository.get_previous_canonical_direction(
        series_key="PRICE.US.CPI",
        observed_on=date(2026, 1, 2),
    )
    append_result = repository.append_trend_change_event(
        {
            "series_key": "PRICE.US.CPI",
            "previous_direction": "up",
            "current_direction": "down",
            "effective_observed_on": date(2026, 1, 2),
            "processing_context": "incremental",
            "visibility_classification": "user_visible",
            "idempotency_fingerprint": "PRICE.US.CPI|2026-01-02|up|down|incremental",
        }
    )
    assert connection.event_row is not None
    fanout_count = repository.fan_out_notifications_for_event(
        event_id=str(connection.event_row["id"])
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
    mark_all_count = repository.mark_all_notifications_read(user_id=str(uuid4()))
    create_missing_dataset = repository.create_or_reactivate_subscription(
        user_id=str(uuid4()),
        dataset_id="MISSING.DATASET",
        now=datetime.now(tz=UTC),
    )
    remove_missing_dataset = repository.remove_active_subscription(
        user_id=str(uuid4()),
        dataset_id="MISSING.DATASET",
        now=datetime.now(tz=UTC),
    )

    assert previous is None
    assert append_result["inserted"] is False
    assert fanout_count == 0
    assert cast(dict[str, Any], listed["pagination"])["has_more"] is True
    assert cast(dict[str, Any], listed["pagination"])["next_cursor"] is not None
    assert mark_read is False
    assert mark_unread is False
    assert mark_all_count == 0
    assert create_missing_dataset is None
    assert remove_missing_dataset is False


def test_notification_repository_retention_deletes_only_read_notifications() -> None:
    connection = _ConnectionDouble()
    connection.retention_delete_rowcount = 3
    repository = _repo(connection)

    deleted = repository.enforce_notification_retention_policy(
        now=datetime.now(tz=UTC),
        retention_days=365,
    )

    assert deleted == 3
    delete_sql = "\n".join(sql for sql, _params in connection.executed)
    assert "DELETE FROM user_trend_notifications" in delete_sql
    assert "unread_state = 'read'" in delete_sql


def test_notification_repository_retention_rejects_invalid_window() -> None:
    repository = _repo(_ConnectionDouble())

    with pytest.raises(ValueError, match="retention_days must be at least 1"):
        repository.enforce_notification_retention_policy(
            now=datetime.now(tz=UTC),
            retention_days=0,
        )
