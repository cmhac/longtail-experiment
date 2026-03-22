"""Postgres-backed repository for canonical observation persistence."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any, Protocol
from uuid import uuid4

from sqlalchemy import Engine, create_engine, text

from .postgres_run_repository import resolve_database_url


class ObservationPayload(Protocol):
    """Structural contract for canonical observation persistence payloads."""

    source_name: str
    source_type: str
    series_key: str
    metric_name: str
    frequency_granularity: str
    observed_on: date
    reported_at: datetime
    value: Decimal
    attributes: dict[str, str]


class PostgresObservationRepository:
    """Persist canonical observations in the shared observation-store tables."""

    def __init__(self, *, database_url: str | None = None) -> None:
        """Initialize repository with a resolved Postgres connection string."""
        self._database_url = resolve_database_url(explicit_url=database_url)
        self._engine: Engine = create_engine(self._database_url, pool_pre_ping=True)

    def upsert_observation(self, observation: ObservationPayload) -> None:
        """Insert or update a canonical observation and its parent data-series row."""
        now = datetime.now(tz=UTC)
        attributes_json = json.dumps(observation.attributes)
        with self._engine.begin() as connection:
            source_profile_id = connection.execute(
                text(
                    """
                    INSERT INTO source_profiles (
                        id,
                        source_name,
                        source_type,
                        frequency_granularity,
                        created_at
                    ) VALUES (
                        :id,
                        :source_name,
                        :source_type,
                        :frequency_granularity,
                        :created_at
                    )
                    ON CONFLICT (source_name) DO UPDATE
                    SET
                        source_type = EXCLUDED.source_type,
                        frequency_granularity = EXCLUDED.frequency_granularity,
                        created_at = EXCLUDED.created_at
                    RETURNING id
                    """
                ),
                {
                    "id": uuid4(),
                    "source_name": observation.source_name,
                    "source_type": observation.source_type,
                    "frequency_granularity": observation.frequency_granularity,
                    "created_at": now,
                },
            ).scalar_one()

            series_id = connection.execute(
                text(
                    """
                    INSERT INTO data_series (
                        id,
                        source_profile_id,
                        series_key,
                        metric_name,
                        default_scale,
                        created_at
                    ) VALUES (
                        :id,
                        :source_profile_id,
                        :series_key,
                        :metric_name,
                        :default_scale,
                        :created_at
                    )
                    ON CONFLICT (series_key) DO UPDATE
                    SET
                        source_profile_id = EXCLUDED.source_profile_id,
                        metric_name = EXCLUDED.metric_name,
                        default_scale = EXCLUDED.default_scale,
                        created_at = EXCLUDED.created_at
                    RETURNING id
                    """
                ),
                {
                    "id": uuid4(),
                    "source_profile_id": source_profile_id,
                    "series_key": observation.series_key,
                    "metric_name": observation.metric_name,
                    "default_scale": 1,
                    "created_at": now,
                },
            ).scalar_one()

            updated = connection.execute(
                text(
                    """
                    UPDATE observations
                    SET
                        value = :value,
                        reported_at = :reported_at,
                        attributes = CAST(:attributes AS JSONB)
                    WHERE
                        series_id = :series_id
                        AND observed_on = :observed_on
                    """
                ),
                {
                    "series_id": series_id,
                    "observed_on": observation.observed_on,
                    "reported_at": observation.reported_at,
                    "value": observation.value,
                    "attributes": attributes_json,
                },
            )
            if updated.rowcount == 0:
                connection.execute(
                    text(
                        """
                        INSERT INTO observations (
                            id,
                            series_id,
                            observed_on,
                            value,
                            reported_at,
                            attributes
                        ) VALUES (
                            :id,
                            :series_id,
                            :observed_on,
                            :value,
                            :reported_at,
                            CAST(:attributes AS JSONB)
                        )
                        """
                    ),
                    {
                        "id": uuid4(),
                        "series_id": series_id,
                        "observed_on": observation.observed_on,
                        "reported_at": observation.reported_at,
                        "value": observation.value,
                        "attributes": attributes_json,
                    },
                )

    def read_latest_observed_on(self, *, series_key: str) -> date | None:
        """Return latest persisted observation date for one canonical series."""
        with self._engine.begin() as connection:
            value = connection.execute(
                text(
                    """
                    SELECT MAX(observed_on)
                    FROM observations o
                    JOIN data_series ds ON ds.id = o.series_id
                    WHERE ds.series_key = :series_key
                    """
                ),
                {"series_key": series_key},
            ).scalar_one_or_none()

        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        return None

    def read_series_observations(self, *, series_key: str) -> list[dict[str, Any]]:
        """Return all observations for one series sorted by observed date."""
        with self._engine.begin() as connection:
            rows = (
                connection.execute(
                    text(
                        """
                        SELECT
                            ds.series_key AS series_key,
                            o.observed_on,
                            o.reported_at,
                            o.value
                        FROM observations o
                        JOIN data_series ds ON ds.id = o.series_id
                        WHERE ds.series_key = :series_key
                        ORDER BY o.observed_on ASC
                        """
                    ),
                    {"series_key": series_key},
                )
                .mappings()
                .all()
            )
        return [dict(row) for row in rows]

    def clear_all(self) -> None:
        """Clear observation-store tables for integration test isolation."""
        with self._engine.begin() as connection:
            connection.execute(text("DELETE FROM observations"))
            connection.execute(text("DELETE FROM data_series"))

    @staticmethod
    def upsert_value(series_key: str, observed_on: date, value: Decimal) -> None:
        """Legacy protocol method intentionally unsupported for this repository."""
        raise NotImplementedError(
            "PostgresObservationRepository requires full canonical observations"
        )
