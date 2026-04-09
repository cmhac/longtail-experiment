"""Postgres repository for trend-change notifications and subscriptions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import Engine, text


def _parse_uuid(value: str) -> UUID:
    return UUID(value)


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


@dataclass(slots=True)
class PostgresNotificationRepository:
    """Persist and query notification-domain data in PostgreSQL."""

    engine: Engine

    def _resolve_series_id(self, *, dataset_id: str) -> UUID | None:
        with self.engine.begin() as connection:
            value = connection.execute(
                text(
                    """
                    SELECT id
                    FROM data_series
                    WHERE series_key = :series_key
                    LIMIT 1
                    """
                ),
                {"series_key": dataset_id},
            ).scalar_one_or_none()
        if value is None:
            return None
        if isinstance(value, UUID):
            return value
        return _parse_uuid(str(value))

    def get_previous_canonical_direction(
        self,
        *,
        series_key: str,
        observed_on: date,
    ) -> str | None:
        """Return latest prior canonical direction before observed date."""

        with self.engine.begin() as connection:
            value = connection.execute(
                text(
                    """
                    SELECT tcd.canonical_direction
                    FROM trend_canonical_descriptors tcd
                    JOIN data_series ds ON ds.id = tcd.data_series_id
                    WHERE ds.series_key = :series_key
                      AND tcd.observed_on < :observed_on
                      AND tcd.canonical_direction IN ('up', 'down')
                    ORDER BY tcd.observed_on DESC, tcd.created_at DESC
                    LIMIT 1
                    """
                ),
                {
                    "series_key": series_key,
                    "observed_on": observed_on,
                },
            ).scalar_one_or_none()
        if value is None:
            return None
        direction = str(value)
        if direction not in {"up", "down"}:
            return None
        return direction

    def append_trend_change_event(
        self, payload: dict[str, object]
    ) -> dict[str, object]:
        """Persist one reversal event idempotently and return event metadata."""

        emitted_at = payload.get("emitted_at")
        now = emitted_at if isinstance(emitted_at, datetime) else datetime.now(tz=UTC)
        with self.engine.begin() as connection:
            inserted = (
                connection.execute(
                    text(
                        """
                        INSERT INTO trend_change_events (
                            id,
                            data_series_id,
                            previous_direction,
                            current_direction,
                            effective_observed_on,
                            processing_context,
                            visibility_classification,
                            idempotency_fingerprint,
                            emitted_at
                        ) VALUES (
                            :id,
                            (
                                SELECT id
                                FROM data_series
                                WHERE series_key = :series_key
                                LIMIT 1
                            ),
                            :previous_direction,
                            :current_direction,
                            :effective_observed_on,
                            :processing_context,
                            :visibility_classification,
                            :idempotency_fingerprint,
                            :emitted_at
                        )
                        ON CONFLICT (idempotency_fingerprint) DO NOTHING
                        RETURNING id
                        """
                    ),
                    {
                        "id": uuid4(),
                        "series_key": payload["series_key"],
                        "previous_direction": payload["previous_direction"],
                        "current_direction": payload["current_direction"],
                        "effective_observed_on": payload["effective_observed_on"],
                        "processing_context": payload["processing_context"],
                        "visibility_classification": payload[
                            "visibility_classification"
                        ],
                        "idempotency_fingerprint": payload["idempotency_fingerprint"],
                        "emitted_at": now,
                    },
                )
                .mappings()
                .first()
            )
            if inserted is not None:
                event_id_value = inserted["id"]
                event_id = (
                    str(event_id_value)
                    if isinstance(event_id_value, UUID)
                    else str(_parse_uuid(str(event_id_value)))
                )
                return {
                    "event_id": event_id,
                    "inserted": True,
                }

            existing = (
                connection.execute(
                    text(
                        """
                        SELECT id
                        FROM trend_change_events
                        WHERE idempotency_fingerprint = :idempotency_fingerprint
                        LIMIT 1
                        """
                    ),
                    {
                        "idempotency_fingerprint": payload["idempotency_fingerprint"],
                    },
                )
                .mappings()
                .first()
            )

        if existing is None:
            raise RuntimeError("failed to resolve idempotent trend change event")

        event_id_value = existing["id"]
        event_id = (
            str(event_id_value)
            if isinstance(event_id_value, UUID)
            else str(_parse_uuid(str(event_id_value)))
        )
        return {
            "event_id": event_id,
            "inserted": False,
        }

    def fan_out_notifications_for_event(self, *, event_id: str) -> int:
        """Fan out one user-visible event to active subscriptions."""

        with self.engine.begin() as connection:
            row = (
                connection.execute(
                    text(
                        """
                    SELECT
                        tce.id,
                        tce.data_series_id,
                        ds.series_key AS dataset_id,
                        tce.previous_direction,
                        tce.current_direction,
                        tce.effective_observed_on,
                        tce.processing_context,
                        tce.visibility_classification,
                        tce.emitted_at
                    FROM trend_change_events tce
                    JOIN data_series ds ON ds.id = tce.data_series_id
                    WHERE tce.id = :event_id
                    LIMIT 1
                    """
                    ),
                    {"event_id": _parse_uuid(event_id)},
                )
                .mappings()
                .first()
            )
            if row is None:
                return 0
            if str(row["visibility_classification"]) != "user_visible":
                return 0

            eligible_rows = (
                connection.execute(
                    text(
                        """
                        SELECT uds.user_id
                        FROM user_dataset_subscriptions uds
                        WHERE uds.data_series_id = :data_series_id
                          AND uds.unsubscribed_at IS NULL
                          AND uds.subscribed_at <= :emitted_at
                        """
                    ),
                    {
                        "data_series_id": row["data_series_id"],
                        "emitted_at": row["emitted_at"],
                    },
                )
                .mappings()
                .all()
            )

            inserted_count = 0
            for eligible in eligible_rows:
                result = connection.execute(
                    text(
                        """
                        INSERT INTO user_trend_notifications (
                            id,
                            event_id,
                            user_id,
                            data_series_id,
                            destination_path,
                            title,
                            body,
                            unread_state,
                            read_at,
                            delivered_at,
                            channel,
                            delivery_status
                        ) VALUES (
                            :id,
                            :event_id,
                            :user_id,
                            :data_series_id,
                            :destination_path,
                            :title,
                            :body,
                            'unread',
                            NULL,
                            :delivered_at,
                            'in_app',
                            'delivered'
                        )
                        ON CONFLICT (event_id, user_id) DO NOTHING
                        """
                    ),
                    {
                        "id": uuid4(),
                        "event_id": _parse_uuid(event_id),
                        "user_id": eligible["user_id"],
                        "data_series_id": row["data_series_id"],
                        "destination_path": f"/datasets/{row['dataset_id']}",
                        "title": "Trend reversal detected",
                        "body": (
                            f"{row['dataset_id']}: {row['previous_direction']} to "
                            f"{row['current_direction']}"
                        ),
                        "delivered_at": datetime.now(tz=UTC),
                    },
                )
                inserted_count += int(result.rowcount or 0)
        return inserted_count

    def list_notifications(
        self,
        *,
        user_id: str,
        page_size: int,
        cursor: str | None,
        unread_only: bool,
    ) -> dict[str, object]:
        """Return one paginated newest-first notification listing payload."""

        conditions = ["utn.user_id = :user_id"]
        params: dict[str, object] = {
            "user_id": _parse_uuid(user_id),
            "limit": page_size + 1,
        }
        if unread_only:
            conditions.append("utn.unread_state = 'unread'")

        cursor_delivered_at: datetime | None = None
        cursor_notification_id: UUID | None = None
        if cursor:
            if "|" in cursor:
                delivered_part, id_part = cursor.split("|", maxsplit=1)
                cursor_delivered_at = _parse_datetime(delivered_part)
                cursor_notification_id = _parse_uuid(id_part)
        if cursor_delivered_at is not None and cursor_notification_id is not None:
            conditions.append(
                "(utn.delivered_at, utn.id) < (:cursor_delivered_at, :cursor_notification_id)"
            )
            params["cursor_delivered_at"] = cursor_delivered_at
            params["cursor_notification_id"] = cursor_notification_id

        where_clause = " AND ".join(conditions)

        with self.engine.begin() as connection:
            rows = (
                connection.execute(
                    text(
                        f"""
                        SELECT
                            utn.id AS notification_id,
                            utn.event_id,
                            ds.series_key AS dataset_id,
                            utn.title,
                            utn.body,
                            utn.destination_path,
                            (utn.unread_state = 'unread') AS unread,
                            utn.read_at,
                            utn.delivered_at,
                            utn.channel,
                            utn.delivery_status,
                            tce.previous_direction,
                            tce.current_direction,
                            tce.effective_observed_on,
                            tce.processing_context,
                            tce.visibility_classification
                        FROM user_trend_notifications utn
                        JOIN trend_change_events tce ON tce.id = utn.event_id
                        JOIN data_series ds ON ds.id = utn.data_series_id
                        WHERE {where_clause}
                        ORDER BY utn.delivered_at DESC, utn.id DESC
                        LIMIT :limit
                        """
                    ),
                    params,
                )
                .mappings()
                .all()
            )

        has_more = len(rows) > page_size
        selected_rows = rows[:page_size]
        next_cursor: str | None = None
        if has_more and selected_rows:
            last = selected_rows[-1]
            delivered_at_value = last["delivered_at"]
            notification_id_value = last["notification_id"]
            delivered_at_text = (
                delivered_at_value.isoformat()
                if isinstance(delivered_at_value, datetime)
                else str(delivered_at_value)
            )
            next_cursor = f"{delivered_at_text}|{notification_id_value}"

        items: list[dict[str, object]] = []
        for row in selected_rows:
            notification_id_value = row["notification_id"]
            event_id_value = row["event_id"]
            items.append(
                {
                    "notification_id": str(notification_id_value),
                    "event_id": str(event_id_value),
                    "dataset_id": str(row["dataset_id"]),
                    "title": str(row["title"]),
                    "body": str(row["body"]),
                    "previous_direction": str(row["previous_direction"]),
                    "current_direction": str(row["current_direction"]),
                    "effective_observed_on": str(row["effective_observed_on"]),
                    "destination_path": str(row["destination_path"]),
                    "unread": bool(row["unread"]),
                    "read_at": (
                        row["read_at"].isoformat()
                        if isinstance(row["read_at"], datetime)
                        else None
                    ),
                    "delivered_at": (
                        row["delivered_at"].isoformat()
                        if isinstance(row["delivered_at"], datetime)
                        else str(row["delivered_at"])
                    ),
                    "channel": str(row["channel"]),
                    "delivery_status": str(row["delivery_status"]),
                    "processing_context": str(row["processing_context"]),
                    "visibility_classification": str(row["visibility_classification"]),
                }
            )

        return {
            "items": items,
            "pagination": {
                "page_size": page_size,
                "has_more": has_more,
                "next_cursor": next_cursor,
            },
        }

    def get_unread_summary(self, *, user_id: str) -> dict[str, object]:
        """Return unread count and latest delivered timestamp for one user."""

        with self.engine.begin() as connection:
            row = (
                connection.execute(
                    text(
                        """
                        SELECT
                            COALESCE(
                                SUM(CASE WHEN unread_state = 'unread' THEN 1 ELSE 0 END),
                                0
                            )::BIGINT AS unread_count,
                            MAX(delivered_at) AS last_notification_at
                        FROM user_trend_notifications
                        WHERE user_id = :user_id
                        """
                    ),
                    {"user_id": _parse_uuid(user_id)},
                )
                .mappings()
                .one()
            )

        last_notification_at = row["last_notification_at"]
        return {
            "unread_count": int(row["unread_count"]),
            "last_notification_at": (
                last_notification_at.isoformat()
                if isinstance(last_notification_at, datetime)
                else None
            ),
            "generated_at": datetime.now(tz=UTC).isoformat(),
        }

    def mark_notification_read(self, *, user_id: str, notification_id: str) -> bool:
        """Mark one notification read for one user."""

        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    UPDATE user_trend_notifications
                    SET
                        unread_state = 'read',
                        read_at = NOW()
                    WHERE id = :notification_id
                      AND user_id = :user_id
                      AND unread_state = 'unread'
                    RETURNING id
                    """
                ),
                {
                    "notification_id": _parse_uuid(notification_id),
                    "user_id": _parse_uuid(user_id),
                },
            ).scalar_one_or_none()
        return row is not None

    def mark_notification_unread(self, *, user_id: str, notification_id: str) -> bool:
        """Mark one notification unread for one user."""

        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    UPDATE user_trend_notifications
                    SET
                        unread_state = 'unread',
                        read_at = NULL
                    WHERE id = :notification_id
                      AND user_id = :user_id
                      AND unread_state = 'read'
                    RETURNING id
                    """
                ),
                {
                    "notification_id": _parse_uuid(notification_id),
                    "user_id": _parse_uuid(user_id),
                },
            ).scalar_one_or_none()
        return row is not None

    def mark_all_notifications_read(self, *, user_id: str) -> int:
        """Mark all unread notifications read for one user."""

        with self.engine.begin() as connection:
            rows = connection.execute(
                text(
                    """
                    UPDATE user_trend_notifications
                    SET
                        unread_state = 'read',
                        read_at = NOW()
                    WHERE user_id = :user_id
                      AND unread_state = 'unread'
                    """
                ),
                {"user_id": _parse_uuid(user_id)},
            )
        return int(rows.rowcount or 0)

    def list_active_subscriptions(self, *, user_id: str) -> list[dict[str, object]]:
        """Return active dataset subscriptions for one user."""

        with self.engine.begin() as connection:
            rows = (
                connection.execute(
                    text(
                        """
                        SELECT
                            ds.series_key AS dataset_id,
                            uds.subscribed_at,
                            uds.unsubscribed_at
                        FROM user_dataset_subscriptions uds
                        JOIN data_series ds ON ds.id = uds.data_series_id
                        WHERE uds.user_id = :user_id
                          AND uds.unsubscribed_at IS NULL
                        ORDER BY uds.subscribed_at DESC, ds.series_key ASC
                        """
                    ),
                    {"user_id": _parse_uuid(user_id)},
                )
                .mappings()
                .all()
            )

        return [
            {
                "dataset_id": str(row["dataset_id"]),
                "subscribed_at": (
                    row["subscribed_at"].isoformat()
                    if isinstance(row["subscribed_at"], datetime)
                    else str(row["subscribed_at"])
                ),
                "unsubscribed_at": None,
            }
            for row in rows
        ]

    def create_or_reactivate_subscription(
        self,
        *,
        user_id: str,
        dataset_id: str,
        now: datetime,
    ) -> dict[str, object] | None:
        """Create or reactivate one dataset subscription for one user."""

        series_id = self._resolve_series_id(dataset_id=dataset_id)
        if series_id is None:
            return None

        with self.engine.begin() as connection:
            existing_active = (
                connection.execute(
                    text(
                        """
                    SELECT id, subscribed_at
                    FROM user_dataset_subscriptions
                    WHERE user_id = :user_id
                      AND data_series_id = :data_series_id
                      AND unsubscribed_at IS NULL
                    LIMIT 1
                    """
                    ),
                    {
                        "user_id": _parse_uuid(user_id),
                        "data_series_id": series_id,
                    },
                )
                .mappings()
                .first()
            )
            if existing_active is not None:
                subscribed_at_value = existing_active["subscribed_at"]
                subscribed_at = (
                    subscribed_at_value.isoformat()
                    if isinstance(subscribed_at_value, datetime)
                    else str(subscribed_at_value)
                )
                return {
                    "dataset_id": dataset_id,
                    "subscribed_at": subscribed_at,
                    "created": False,
                }

            existing_inactive = (
                connection.execute(
                    text(
                        """
                    SELECT id
                    FROM user_dataset_subscriptions
                    WHERE user_id = :user_id
                      AND data_series_id = :data_series_id
                    ORDER BY subscribed_at DESC
                    LIMIT 1
                    """
                    ),
                    {
                        "user_id": _parse_uuid(user_id),
                        "data_series_id": series_id,
                    },
                )
                .mappings()
                .first()
            )
            if existing_inactive is not None:
                connection.execute(
                    text(
                        """
                        UPDATE user_dataset_subscriptions
                        SET
                            subscribed_at = :subscribed_at,
                            unsubscribed_at = NULL,
                            updated_at = :updated_at
                        WHERE id = :id
                        """
                    ),
                    {
                        "id": existing_inactive["id"],
                        "subscribed_at": now,
                        "updated_at": now,
                    },
                )
                return {
                    "dataset_id": dataset_id,
                    "subscribed_at": now.isoformat(),
                    "created": True,
                }

            connection.execute(
                text(
                    """
                    INSERT INTO user_dataset_subscriptions (
                        id,
                        user_id,
                        data_series_id,
                        subscribed_at,
                        unsubscribed_at,
                        updated_at
                    ) VALUES (
                        :id,
                        :user_id,
                        :data_series_id,
                        :subscribed_at,
                        NULL,
                        :updated_at
                    )
                    """
                ),
                {
                    "id": uuid4(),
                    "user_id": _parse_uuid(user_id),
                    "data_series_id": series_id,
                    "subscribed_at": now,
                    "updated_at": now,
                },
            )

        return {
            "dataset_id": dataset_id,
            "subscribed_at": now.isoformat(),
            "created": True,
        }

    def remove_active_subscription(
        self,
        *,
        user_id: str,
        dataset_id: str,
        now: datetime,
    ) -> bool:
        """Deactivate one dataset subscription when currently active."""

        series_id = self._resolve_series_id(dataset_id=dataset_id)
        if series_id is None:
            return False

        with self.engine.begin() as connection:
            rows = connection.execute(
                text(
                    """
                    UPDATE user_dataset_subscriptions
                    SET
                        unsubscribed_at = :unsubscribed_at,
                        updated_at = :updated_at
                    WHERE user_id = :user_id
                      AND data_series_id = :data_series_id
                      AND unsubscribed_at IS NULL
                    """
                ),
                {
                    "user_id": _parse_uuid(user_id),
                    "data_series_id": series_id,
                    "unsubscribed_at": now,
                    "updated_at": now,
                },
            )
        return int(rows.rowcount or 0) > 0

    def enforce_notification_retention_policy(
        self,
        *,
        now: datetime,
        retention_days: int = 365,
    ) -> int:
        """Delete read notifications older than retention window and return count."""

        if retention_days < 1:
            raise ValueError("retention_days must be at least 1")

        cutoff = now - timedelta(days=retention_days)
        with self.engine.begin() as connection:
            rows = connection.execute(
                text(
                    """
                    DELETE FROM user_trend_notifications
                    WHERE unread_state = 'read'
                      AND delivered_at < :cutoff
                    """
                ),
                {"cutoff": cutoff},
            )
        return int(rows.rowcount or 0)
