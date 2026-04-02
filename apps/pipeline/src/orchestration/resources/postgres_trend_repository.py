"""Postgres repository for trend lifecycle rows and transition audit events."""

from __future__ import annotations

import json
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

    def count_canonical_descriptors_for_series(self, *, series_key: str) -> int:
        """Return persisted canonical descriptor count for one canonical series key."""
        with self._engine.begin() as connection:
            count_value = connection.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM trend_canonical_descriptors tcd
                    JOIN data_series ds ON ds.id = tcd.data_series_id
                    WHERE ds.series_key = :series_key
                    """
                ),
                {"series_key": series_key},
            ).scalar_one()
        return int(count_value)

    def upsert_lookback_applicability(self, payload: dict[str, object]) -> None:
        """Persist one lookback applicability row keyed by series/observation/lookback."""
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO trend_lookback_evaluations (
                        id,
                        data_series_id,
                        observation_id,
                        lookback_points,
                        applicability_state,
                        reason_code,
                        reason_detail,
                        created_at
                    ) VALUES (
                        :id,
                        (
                            SELECT id FROM data_series WHERE series_key = :series_key
                        ),
                        COALESCE(
                            CAST(:observation_id AS UUID),
                            (
                                SELECT o.id
                                FROM observations o
                                JOIN data_series ds ON ds.id = o.series_id
                                WHERE ds.series_key = :series_key
                                  AND o.observed_on = :observed_on
                                ORDER BY o.reported_at DESC
                                LIMIT 1
                            )
                        ),
                        :lookback_points,
                        :applicability_state,
                        :reason_code,
                        :reason_detail,
                        :created_at
                    )
                    ON CONFLICT (
                        data_series_id,
                        observation_id,
                        lookback_points
                    )
                    DO UPDATE SET
                        applicability_state = EXCLUDED.applicability_state,
                        reason_code = EXCLUDED.reason_code,
                        reason_detail = EXCLUDED.reason_detail
                    """
                ),
                {
                    "id": uuid4(),
                    "series_key": payload["series_key"],
                    "observed_on": payload["observed_on"],
                    "observation_id": payload.get("observation_id"),
                    "lookback_points": payload["lookback_points"],
                    "applicability_state": payload["applicability_state"],
                    "reason_code": payload["reason_code"],
                    "reason_detail": payload["reason_detail"],
                    "created_at": datetime.now(tz=UTC),
                },
            )

    def upsert_lookback_snapshot(self, payload: dict[str, object]) -> None:
        """Persist one lookback snapshot row keyed by series/observation/lookback."""
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO trend_lookback_snapshots (
                        id,
                        data_series_id,
                        observation_id,
                        observed_on,
                        lookback_points,
                        outcome_state,
                        trend_label,
                        direction,
                        strength,
                        seasonality_classification,
                        analysis_version,
                        created_at
                    ) VALUES (
                        :id,
                        (
                            SELECT id FROM data_series WHERE series_key = :series_key
                        ),
                        COALESCE(
                            CAST(:observation_id AS UUID),
                            (
                                SELECT o.id
                                FROM observations o
                                JOIN data_series ds ON ds.id = o.series_id
                                WHERE ds.series_key = :series_key
                                  AND o.observed_on = :observed_on
                                ORDER BY o.reported_at DESC
                                LIMIT 1
                            )
                        ),
                        :observed_on,
                        :lookback_points,
                        :outcome_state,
                        :trend_label,
                        :direction,
                        :strength,
                        :seasonality_classification,
                        :analysis_version,
                        :created_at
                    )
                    ON CONFLICT (
                        data_series_id,
                        observation_id,
                        lookback_points
                    )
                    DO UPDATE SET
                        observed_on = EXCLUDED.observed_on,
                        outcome_state = EXCLUDED.outcome_state,
                        trend_label = EXCLUDED.trend_label,
                        direction = EXCLUDED.direction,
                        strength = EXCLUDED.strength,
                        seasonality_classification = EXCLUDED.seasonality_classification,
                        analysis_version = EXCLUDED.analysis_version
                    """
                ),
                {
                    "id": uuid4(),
                    "series_key": payload["series_key"],
                    "observed_on": payload["observed_on"],
                    "observation_id": payload.get("observation_id"),
                    "lookback_points": payload["lookback_points"],
                    "outcome_state": payload["outcome_state"],
                    "trend_label": payload["trend_label"],
                    "direction": payload["direction"],
                    "strength": payload["strength"],
                    "seasonality_classification": payload["seasonality_classification"],
                    "analysis_version": payload["analysis_version"],
                    "created_at": datetime.now(tz=UTC),
                },
            )

    def upsert_canonical_descriptor(self, payload: dict[str, object]) -> None:
        """Persist one canonical descriptor row keyed by series/observation."""
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO trend_canonical_descriptors (
                        id,
                        data_series_id,
                        observation_id,
                        observed_on,
                        descriptor_state,
                        canonical_trend_label,
                        canonical_direction,
                        canonical_strength,
                        selected_lookback_points,
                        weighting_version,
                        weighting_trace,
                        created_at
                    ) VALUES (
                        :id,
                        (
                            SELECT id FROM data_series WHERE series_key = :series_key
                        ),
                        COALESCE(
                            CAST(:observation_id AS UUID),
                            (
                                SELECT o.id
                                FROM observations o
                                JOIN data_series ds ON ds.id = o.series_id
                                WHERE ds.series_key = :series_key
                                  AND o.observed_on = :observed_on
                                ORDER BY o.reported_at DESC
                                LIMIT 1
                            )
                        ),
                        :observed_on,
                        :descriptor_state,
                        :canonical_trend_label,
                        :canonical_direction,
                        :canonical_strength,
                        :selected_lookback_points,
                        :weighting_version,
                        CAST(:weighting_trace AS JSONB),
                        :created_at
                    )
                    ON CONFLICT (
                        data_series_id,
                        observation_id
                    )
                    DO UPDATE SET
                        observed_on = EXCLUDED.observed_on,
                        descriptor_state = EXCLUDED.descriptor_state,
                        canonical_trend_label = EXCLUDED.canonical_trend_label,
                        canonical_direction = EXCLUDED.canonical_direction,
                        canonical_strength = EXCLUDED.canonical_strength,
                        selected_lookback_points = EXCLUDED.selected_lookback_points,
                        weighting_version = EXCLUDED.weighting_version,
                        weighting_trace = EXCLUDED.weighting_trace
                    """
                ),
                {
                    "id": uuid4(),
                    "series_key": payload["series_key"],
                    "observed_on": payload["observed_on"],
                    "observation_id": payload.get("observation_id"),
                    "descriptor_state": payload["descriptor_state"],
                    "canonical_trend_label": payload["canonical_trend_label"],
                    "canonical_direction": payload["canonical_direction"],
                    "canonical_strength": payload["canonical_strength"],
                    "selected_lookback_points": payload["selected_lookback_points"],
                    "weighting_version": payload["weighting_version"],
                    "weighting_trace": (
                        None
                        if payload["weighting_trace"] is None
                        else json.dumps(payload["weighting_trace"])
                    ),
                    "created_at": datetime.now(tz=UTC),
                },
            )
