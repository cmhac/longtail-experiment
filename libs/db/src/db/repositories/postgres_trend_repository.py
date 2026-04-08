"""Postgres repository for trend lifecycle rows and transition audit events."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Engine, create_engine, text

from .interfaces import TrendLifecycleRepository


def _parse_uuid(value: str) -> UUID:
    return UUID(value)


class PostgresTrendRepository(TrendLifecycleRepository):
    """Persist and read trend lifecycle records in PostgreSQL."""

    def __init__(self, *, database_url: str) -> None:
        """Initialize repository with explicit Postgres connection URL."""

        self._engine: Engine = create_engine(database_url, pool_pre_ping=True)

    def get_ongoing_trend_for_series(
        self, *, series_key: str
    ) -> dict[str, object] | None:
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
            count_value: Any = connection.execute(
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
        """Return persisted canonical descriptor count for one series key."""

        with self._engine.begin() as connection:
            count_value: Any = connection.execute(
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
                        descriptor_state,
                        trend_label,
                        direction,
                        confidence_score,
                        dominant_measure_family,
                        theil_sen_slope,
                        theil_sen_low_slope,
                        theil_sen_high_slope,
                        kendall_tau,
                        kendall_pvalue,
                        ols_slope,
                        ols_intercept,
                        ols_r_squared,
                        ols_pvalue,
                        preprocessing,
                        reason_code,
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
                        :descriptor_state,
                        :trend_label,
                        :direction,
                        :confidence_score,
                        :dominant_measure_family,
                        :theil_sen_slope,
                        :theil_sen_low_slope,
                        :theil_sen_high_slope,
                        :kendall_tau,
                        :kendall_pvalue,
                        :ols_slope,
                        :ols_intercept,
                        :ols_r_squared,
                        :ols_pvalue,
                        CAST(:preprocessing AS JSONB),
                        :reason_code,
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
                        descriptor_state = EXCLUDED.descriptor_state,
                        trend_label = EXCLUDED.trend_label,
                        direction = EXCLUDED.direction,
                        confidence_score = EXCLUDED.confidence_score,
                        dominant_measure_family = EXCLUDED.dominant_measure_family,
                        theil_sen_slope = EXCLUDED.theil_sen_slope,
                        theil_sen_low_slope = EXCLUDED.theil_sen_low_slope,
                        theil_sen_high_slope = EXCLUDED.theil_sen_high_slope,
                        kendall_tau = EXCLUDED.kendall_tau,
                        kendall_pvalue = EXCLUDED.kendall_pvalue,
                        ols_slope = EXCLUDED.ols_slope,
                        ols_intercept = EXCLUDED.ols_intercept,
                        ols_r_squared = EXCLUDED.ols_r_squared,
                        ols_pvalue = EXCLUDED.ols_pvalue,
                        preprocessing = EXCLUDED.preprocessing,
                        reason_code = EXCLUDED.reason_code,
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
                    "descriptor_state": payload.get("descriptor_state", "available"),
                    "trend_label": payload["trend_label"],
                    "direction": payload["direction"],
                    "confidence_score": payload.get("confidence_score"),
                    "dominant_measure_family": payload.get("dominant_measure_family"),
                    "theil_sen_slope": payload.get("theil_sen_slope"),
                    "theil_sen_low_slope": payload.get("theil_sen_low_slope"),
                    "theil_sen_high_slope": payload.get("theil_sen_high_slope"),
                    "kendall_tau": payload.get("kendall_tau"),
                    "kendall_pvalue": payload.get("kendall_pvalue"),
                    "ols_slope": payload.get("ols_slope"),
                    "ols_intercept": payload.get("ols_intercept"),
                    "ols_r_squared": payload.get("ols_r_squared"),
                    "ols_pvalue": payload.get("ols_pvalue"),
                    "preprocessing": (
                        None
                        if payload.get("preprocessing") is None
                        else json.dumps(payload["preprocessing"])
                    ),
                    "reason_code": payload.get("reason_code"),
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
                        descriptor_version,
                        descriptor_state,
                        canonical_trend_label,
                        canonical_direction,
                        confidence_score,
                        dominant_measure_family,
                        medium_horizon_weight,
                        short_horizon_weight,
                        long_horizon_weight,
                        preprocessing,
                        ols_slope,
                        ols_intercept,
                        ols_r_squared,
                        ols_pvalue,
                        reason_code,
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
                        :descriptor_version,
                        :descriptor_state,
                        :canonical_trend_label,
                        :canonical_direction,
                        :confidence_score,
                        :dominant_measure_family,
                        :medium_horizon_weight,
                        :short_horizon_weight,
                        :long_horizon_weight,
                        CAST(:preprocessing AS JSONB),
                        :ols_slope,
                        :ols_intercept,
                        :ols_r_squared,
                        :ols_pvalue,
                        :reason_code,
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
                        descriptor_version = EXCLUDED.descriptor_version,
                        descriptor_state = EXCLUDED.descriptor_state,
                        canonical_trend_label = EXCLUDED.canonical_trend_label,
                        canonical_direction = EXCLUDED.canonical_direction,
                        confidence_score = EXCLUDED.confidence_score,
                        dominant_measure_family = EXCLUDED.dominant_measure_family,
                        medium_horizon_weight = EXCLUDED.medium_horizon_weight,
                        short_horizon_weight = EXCLUDED.short_horizon_weight,
                        long_horizon_weight = EXCLUDED.long_horizon_weight,
                        preprocessing = EXCLUDED.preprocessing,
                        ols_slope = EXCLUDED.ols_slope,
                        ols_intercept = EXCLUDED.ols_intercept,
                        ols_r_squared = EXCLUDED.ols_r_squared,
                        ols_pvalue = EXCLUDED.ols_pvalue,
                        reason_code = EXCLUDED.reason_code,
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
                    "descriptor_version": payload.get("descriptor_version", "v2"),
                    "descriptor_state": payload["descriptor_state"],
                    "canonical_trend_label": payload["canonical_trend_label"],
                    "canonical_direction": payload["canonical_direction"],
                    "confidence_score": payload.get("confidence_score"),
                    "dominant_measure_family": payload.get("dominant_measure_family"),
                    "medium_horizon_weight": payload.get("medium_horizon_weight"),
                    "short_horizon_weight": payload.get("short_horizon_weight"),
                    "long_horizon_weight": payload.get("long_horizon_weight"),
                    "preprocessing": (
                        None
                        if payload.get("preprocessing") is None
                        else json.dumps(payload["preprocessing"])
                    ),
                    "ols_slope": payload.get("ols_slope"),
                    "ols_intercept": payload.get("ols_intercept"),
                    "ols_r_squared": payload.get("ols_r_squared"),
                    "ols_pvalue": payload.get("ols_pvalue"),
                    "reason_code": payload.get("reason_code"),
                    "canonical_strength": payload.get("canonical_strength"),
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

    def get_previous_canonical_direction(
        self,
        *,
        series_key: str,
        observed_on: object,
    ) -> str | None:
        """Return latest canonical direction prior to one observed date."""

        with self._engine.begin() as connection:
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
        """Persist one trend-change event idempotently and return event metadata."""

        with self._engine.begin() as connection:
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
                        "emitted_at": payload["emitted_at"],
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

        with self._engine.begin() as connection:
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
                        JOIN user_accounts ua ON ua.id = uds.user_id
                        WHERE uds.data_series_id = :data_series_id
                          AND uds.unsubscribed_at IS NULL
                          AND uds.subscribed_at <= :emitted_at
                          AND ua.account_status = 'active'
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
