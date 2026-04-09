"""Backend persisted repository adapter for trend notification workflows."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Engine, text


class PersistedTrendNotificationRepository:
    """Read/write trend notifications from PostgreSQL runtime storage."""

    def __init__(self, *, engine: Engine) -> None:
        """Initialize with a SQLAlchemy engine for database access."""
        self._engine = engine

    def _resolve_series_id(self, *, dataset_id: str) -> UUID | None:
        with self._engine.begin() as connection:
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
        return UUID(str(value))

    def list_notifications(
        self,
        *,
        user_id: str,
        page_size: int,
        cursor: str | None,
        unread_only: bool,
    ) -> dict[str, object]:
        """Return one newest-first paginated notification payload."""
        conditions = ["utn.user_id = :user_id"]
        params: dict[str, object] = {
            "user_id": UUID(user_id),
            "limit": page_size + 1,
        }
        if unread_only:
            conditions.append("utn.unread_state = 'unread'")

        if cursor and "|" in cursor:
            delivered_part, id_part = cursor.split("|", maxsplit=1)
            conditions.append(
                "(utn.delivered_at, utn.id) < (:cursor_delivered_at, :cursor_notification_id)"
            )
            params["cursor_delivered_at"] = datetime.fromisoformat(delivered_part)
            params["cursor_notification_id"] = UUID(id_part)

        where_clause = " AND ".join(conditions)

        with self._engine.begin() as connection:
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
                            tcd.confidence_score,
                            tce.effective_observed_on,
                            tce.processing_context,
                            tce.visibility_classification
                        FROM user_trend_notifications utn
                        JOIN trend_change_events tce ON tce.id = utn.event_id
                        JOIN data_series ds ON ds.id = utn.data_series_id
                        LEFT JOIN trend_canonical_descriptors tcd
                          ON tcd.data_series_id = tce.data_series_id
                         AND tcd.observed_on = tce.effective_observed_on
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
            next_cursor = f"{last['delivered_at'].isoformat()}|{last['notification_id']}"

        items: list[dict[str, object]] = []
        for row in selected_rows:
            items.append(
                {
                    "notification_id": str(row["notification_id"]),
                    "event_id": str(row["event_id"]),
                    "dataset_id": str(row["dataset_id"]),
                    "title": str(row["title"]),
                    "body": str(row["body"]),
                    "previous_direction": str(row["previous_direction"]),
                    "current_direction": str(row["current_direction"]),
                    "confidence_score": (
                        float(row["confidence_score"])
                        if row.get("confidence_score") is not None
                        else None
                    ),
                    "effective_observed_on": str(row["effective_observed_on"]),
                    "destination_path": str(row["destination_path"]),
                    "unread": bool(row["unread"]),
                    "read_at": (
                        row["read_at"].isoformat() if isinstance(row["read_at"], datetime) else None
                    ),
                    "delivered_at": row["delivered_at"].isoformat(),
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
        """Return unread summary payload for one user."""
        with self._engine.begin() as connection:
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
                    {"user_id": UUID(user_id)},
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
        with self._engine.begin() as connection:
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
                    "notification_id": UUID(notification_id),
                    "user_id": UUID(user_id),
                },
            ).scalar_one_or_none()
        return row is not None

    def mark_notification_unread(self, *, user_id: str, notification_id: str) -> bool:
        """Mark one notification unread for one user."""
        with self._engine.begin() as connection:
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
                    "notification_id": UUID(notification_id),
                    "user_id": UUID(user_id),
                },
            ).scalar_one_or_none()
        return row is not None

    def mark_all_notifications_read(self, *, user_id: str) -> int:
        """Mark all unread notifications read for one user."""
        with self._engine.begin() as connection:
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
                {"user_id": UUID(user_id)},
            )
        return int(rows.rowcount or 0)

    def list_active_subscriptions(self, *, user_id: str) -> list[dict[str, object]]:
        """Return active dataset subscriptions for one user."""
        with self._engine.begin() as connection:
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
                    {"user_id": UUID(user_id)},
                )
                .mappings()
                .all()
            )

        return [
            {
                "dataset_id": str(row["dataset_id"]),
                "subscribed_at": row["subscribed_at"].isoformat(),
                "unsubscribed_at": None,
            }
            for row in rows
        ]

    def create_or_reactivate_subscription(
        self,
        *,
        user_id: str,
        dataset_id: str,
    ) -> dict[str, object] | None:
        """Create or reactivate one dataset subscription."""
        now = datetime.now(tz=UTC)
        series_id = self._resolve_series_id(dataset_id=dataset_id)
        if series_id is None:
            return None

        with self._engine.begin() as connection:
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
                        "user_id": UUID(user_id),
                        "data_series_id": series_id,
                    },
                )
                .mappings()
                .first()
            )
            if existing_active is not None:
                return {
                    "dataset_id": dataset_id,
                    "subscribed_at": existing_active["subscribed_at"].isoformat(),
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
                        "user_id": UUID(user_id),
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
                    "user_id": UUID(user_id),
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

    def remove_active_subscription(self, *, user_id: str, dataset_id: str) -> bool:
        """Remove one active dataset subscription when present."""
        now = datetime.now(tz=UTC)
        series_id = self._resolve_series_id(dataset_id=dataset_id)
        if series_id is None:
            return False

        with self._engine.begin() as connection:
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
                    "user_id": UUID(user_id),
                    "data_series_id": series_id,
                    "unsubscribed_at": now,
                    "updated_at": now,
                },
            )
        return int(rows.rowcount or 0) > 0
