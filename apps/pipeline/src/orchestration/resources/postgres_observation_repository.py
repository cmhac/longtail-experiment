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

    source_key: str
    source_name: str
    source_title: str
    source_description: str
    source_type: str
    series_key: str
    metric_name: str
    observed_on: date
    reported_at: datetime
    value: Decimal
    unit_type: str | None
    attributes: dict[str, str]


def _normalize_optional_text(value: object) -> str | None:
    """Return a stripped string value or None when missing/blank."""
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _normalize_topic_tags(raw_tags: object) -> list[str]:
    """Normalize tag payloads into stable lowercase unique values."""
    if not isinstance(raw_tags, list):
        return []

    normalized: list[str] = []
    seen: set[str] = set()
    for tag in raw_tags:
        if not isinstance(tag, str):
            continue
        value = tag.strip().lower()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


class PostgresObservationRepository:
    """Persist canonical observations in the shared observation-store tables."""

    def __init__(self, *, database_url: str | None = None) -> None:
        """Initialize repository with a resolved Postgres connection string."""
        self._database_url = resolve_database_url(explicit_url=database_url)
        self._engine: Engine = create_engine(self._database_url, pool_pre_ping=True)

    @staticmethod
    def _upsert_source_profile(
        connection: Any,
        *,
        source_profile: dict[str, str],
        created_at: datetime,
    ) -> object:
        return connection.execute(
            text(
                """
                INSERT INTO source_profiles (
                    id,
                    source_key,
                    source_name,
                    source_type,
                    title,
                    description,
                    created_at
                ) VALUES (
                    :id,
                    :source_key,
                    :source_name,
                    :source_type,
                    :title,
                    :description,
                    :created_at
                )
                ON CONFLICT (source_key) DO UPDATE
                SET
                    source_name = EXCLUDED.source_name,
                    source_type = EXCLUDED.source_type,
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    created_at = EXCLUDED.created_at
                RETURNING id
                """
            ),
            {
                "id": uuid4(),
                "source_key": source_profile["source_key"],
                "source_name": source_profile["source_name"],
                "source_type": source_profile["source_type"],
                "title": source_profile["source_title"],
                "description": source_profile["source_description"],
                "created_at": created_at,
            },
        ).scalar_one()

    def upsert_source_profile(
        self,
        *,
        source_key: str,
        source_name: str,
        source_title: str,
        source_description: str,
        source_type: str,
    ) -> None:
        """Persist source-level metadata even when no observations are written."""
        with self._engine.begin() as connection:
            self._upsert_source_profile(
                connection,
                source_profile={
                    "source_key": source_key,
                    "source_name": source_name,
                    "source_title": source_title,
                    "source_description": source_description,
                    "source_type": source_type,
                },
                created_at=datetime.now(tz=UTC),
            )

    def upsert_observation(self, observation: ObservationPayload) -> None:
        """Insert or update a canonical observation and its parent data-series row."""
        now = datetime.now(tz=UTC)
        persisted_attributes = dict(observation.attributes)
        if observation.unit_type is not None and observation.unit_type.strip() != "":
            persisted_attributes.setdefault("unit_type", observation.unit_type)
        attributes_json = json.dumps(persisted_attributes)
        dataset_title = _normalize_optional_text(getattr(observation, "dataset_title", None))
        dataset_description = _normalize_optional_text(
            getattr(observation, "dataset_description", None)
        )
        dataset_geographic_scope = _normalize_optional_text(
            getattr(observation, "dataset_geographic_scope", None)
        )
        topic_tags = _normalize_topic_tags(getattr(observation, "topic_tags", []))
        with self._engine.begin() as connection:
            source_profile_id = self._upsert_source_profile(
                connection,
                source_profile={
                    "source_key": observation.source_key,
                    "source_name": observation.source_name,
                    "source_title": observation.source_title,
                    "source_description": observation.source_description,
                    "source_type": observation.source_type,
                },
                created_at=now,
            )

            series_id = connection.execute(
                text(
                    """
                    INSERT INTO data_series (
                        id,
                        source_profile_id,
                        series_key,
                        metric_name,
                        title,
                        description,
                        geographic_scope,
                        default_scale,
                        created_at
                    ) VALUES (
                        :id,
                        :source_profile_id,
                        :series_key,
                        :metric_name,
                        :title,
                        :description,
                        :geographic_scope,
                        :default_scale,
                        :created_at
                    )
                    ON CONFLICT (series_key) DO UPDATE
                    SET
                        source_profile_id = EXCLUDED.source_profile_id,
                        metric_name = EXCLUDED.metric_name,
                        title = EXCLUDED.title,
                        description = COALESCE(EXCLUDED.description, data_series.description),
                        geographic_scope = COALESCE(
                            EXCLUDED.geographic_scope,
                            data_series.geographic_scope
                        ),
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
                    "title": dataset_title or observation.metric_name,
                    "description": dataset_description,
                    "geographic_scope": dataset_geographic_scope,
                    "default_scale": 1,
                    "created_at": now,
                },
            ).scalar_one()

            for topic_tag in topic_tags:
                topic_tag_id = connection.execute(
                    text(
                        """
                        INSERT INTO topic_tags (
                            id,
                            tag_name,
                            created_at
                        ) VALUES (
                            :id,
                            :tag_name,
                            :created_at
                        )
                        ON CONFLICT (tag_name) DO UPDATE
                        SET tag_name = EXCLUDED.tag_name
                        RETURNING id
                        """
                    ),
                    {
                        "id": uuid4(),
                        "tag_name": topic_tag,
                        "created_at": now,
                    },
                ).scalar_one()

                connection.execute(
                    text(
                        """
                        INSERT INTO data_series_topic_tags (
                            data_series_id,
                            topic_tag_id
                        ) VALUES (
                            :data_series_id,
                            :topic_tag_id
                        )
                        ON CONFLICT DO NOTHING
                        """
                    ),
                    {
                        "data_series_id": series_id,
                        "topic_tag_id": topic_tag_id,
                    },
                )

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
