"""Postgres repository for trend lifecycle rows and transition audit events."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Engine, create_engine, text

from .postgres_run_repository import resolve_database_url


def _parse_uuid(value: str) -> UUID:
    return UUID(value)


class PostgresTrendRepository:
    """Persist and read trend lifecycle records in PostgreSQL."""

    def __init__(self, *, database_url: str | None = None) -> None:
        """Initialize repository with resolved Postgres connection URL."""
        self._engine: Engine = create_engine(
            resolve_database_url(explicit_url=database_url),
            pool_pre_ping=True,
        )

    def get_ongoing_trend_for_series(self, *, series_key: str) -> dict[str, object] | None:
        """Return one ongoing trend snapshot for a series when present."""
        with self._engine.begin() as connection:
            row = (
                connection.execute(
                    text(
                        """
                        SELECT
                            tr.id,
                            tr.trend_label,
                            tr.direction,
                            tr.strength,
                            tr.seasonality_classification
                        FROM trend_records tr
                        JOIN data_series ds ON ds.id = tr.data_series_id
                        WHERE ds.series_key = :series_key
                          AND tr.is_ongoing = TRUE
                        ORDER BY tr.created_at DESC
                        LIMIT 1
                        """
                    ),
                    {"series_key": series_key},
                )
                .mappings()
                .first()
            )
        if row is None:
            return None
        return dict(row)

    def upsert_trend_record(self, payload: dict[str, object]) -> str:
        """Insert one trend record row and return its canonical identifier."""
        now = datetime.now(tz=UTC)
        with self._engine.begin() as connection:
            row_id = connection.execute(
                text(
                    """
                    INSERT INTO trend_records (
                        id,
                        data_series_id,
                        trend_label,
                        direction,
                        strength,
                        seasonality_classification,
                        start_period,
                        end_period,
                        is_ongoing,
                        created_at,
                        ended_at
                    ) VALUES (
                        :id,
                        (
                            SELECT id
                            FROM data_series
                            WHERE series_key = :series_key
                        ),
                        :trend_label,
                        :direction,
                        :strength,
                        :seasonality_classification,
                        :start_period,
                        :end_period,
                        :is_ongoing,
                        :created_at,
                        :ended_at
                    )
                    RETURNING id
                    """
                ),
                {
                    "id": uuid4(),
                    "series_key": payload["series_key"],
                    "trend_label": payload["trend_label"],
                    "direction": payload["direction"],
                    "strength": payload["strength"],
                    "seasonality_classification": payload["seasonality_classification"],
                    "start_period": payload["start_period"],
                    "end_period": payload["end_period"],
                    "is_ongoing": payload["is_ongoing"],
                    "created_at": now,
                    "ended_at": now if payload["end_period"] is not None else None,
                },
            ).scalar_one()

        if isinstance(row_id, UUID):
            return str(row_id)
        return str(_parse_uuid(str(row_id)))

    def close_ongoing_trend_for_series(
        self,
        *,
        series_key: str,
        end_period: datetime,
    ) -> str | None:
        """Close current ongoing trend for a series and return the closed record id."""
        with self._engine.begin() as connection:
            row_id = connection.execute(
                text(
                    """
                    UPDATE trend_records
                    SET
                        end_period = :end_period,
                        is_ongoing = FALSE,
                        ended_at = :ended_at
                    WHERE id = (
                        SELECT tr.id
                        FROM trend_records tr
                        JOIN data_series ds ON ds.id = tr.data_series_id
                        WHERE ds.series_key = :series_key
                          AND tr.is_ongoing = TRUE
                        ORDER BY tr.created_at DESC
                        LIMIT 1
                    )
                    RETURNING id
                    """
                ),
                {
                    "series_key": series_key,
                    "end_period": end_period,
                    "ended_at": datetime.now(tz=UTC),
                },
            ).scalar_one_or_none()

        if row_id is None:
            return None
        if isinstance(row_id, UUID):
            return str(row_id)
        return str(_parse_uuid(str(row_id)))

    def append_transition(self, payload: dict[str, object]) -> None:
        """Append one immutable transition event row."""
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO trend_transition_events (
                        id,
                        data_series_id,
                        transition_type,
                        prior_trend_record_id,
                        new_trend_record_id,
                        trigger_observation_on,
                        reason,
                        created_at
                    ) VALUES (
                        :id,
                        (
                            SELECT id
                            FROM data_series
                            WHERE series_key = :series_key
                        ),
                        :transition_type,
                        :prior_trend_record_id,
                        :new_trend_record_id,
                        :trigger_observation_on,
                        :reason,
                        :created_at
                    )
                    """
                ),
                {
                    "id": uuid4(),
                    "series_key": payload["series_key"],
                    "transition_type": payload["transition_type"],
                    "prior_trend_record_id": (
                        _parse_uuid(str(payload["prior_trend_record_id"]))
                        if payload["prior_trend_record_id"] is not None
                        else None
                    ),
                    "new_trend_record_id": (
                        _parse_uuid(str(payload["new_trend_record_id"]))
                        if payload["new_trend_record_id"] is not None
                        else None
                    ),
                    "trigger_observation_on": payload["trigger_observation_on"],
                    "reason": payload["reason"],
                    "created_at": datetime.now(tz=UTC),
                },
            )

    def count_trend_records_for_series(self, *, series_key: str) -> int:
        """Return total trend record count for one series key."""
        with self._engine.begin() as connection:
            count_value = connection.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM trend_records tr
                    JOIN data_series ds ON ds.id = tr.data_series_id
                    WHERE ds.series_key = :series_key
                    """
                ),
                {"series_key": series_key},
            ).scalar_one()
        return int(count_value)
