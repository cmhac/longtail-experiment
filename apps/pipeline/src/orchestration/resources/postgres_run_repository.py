"""Postgres-backed repository for ingest run outcomes."""

from __future__ import annotations

import os
from collections.abc import Mapping
from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from sqlalchemy import Engine, create_engine, text

if TYPE_CHECKING:
    from src.orchestration.jobs.run_coordinator import RunSummary


def _env_value(environment: Mapping[str, str], key: str, default: str) -> str:
    value = environment.get(key)
    if value is None or value == "":
        return default
    return value


def _build_local_database_url(*, environment: Mapping[str, str]) -> str:
    user = _env_value(environment, "LOCAL_DB_USER", "longtail")
    password = _env_value(environment, "LOCAL_DB_PASSWORD", "longtail")
    host = _env_value(environment, "LOCAL_DB_HOST", "127.0.0.1")
    port = _env_value(environment, "LOCAL_DB_PORT", "55432")
    name = _env_value(environment, "LOCAL_DB_NAME", "longtail_local")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


def resolve_database_url(
    *,
    explicit_url: str | None,
    environment: Mapping[str, str] | None = None,
) -> str:
    """Resolve DB URL preferring env DATABASE_URL then explicit URL then LOCAL_DB defaults."""
    env = environment or os.environ
    direct_override = env.get("DATABASE_URL")
    if direct_override:
        return direct_override
    if explicit_url:
        return explicit_url
    return _build_local_database_url(environment=env)


class PostgresRunRepository:
    """Persist run summaries and source outcomes to runtime ingestion tables."""

    def __init__(self, *, database_url: str | None = None) -> None:
        """Initialize repository engine against configured Postgres runtime DB."""
        self._database_url = resolve_database_url(explicit_url=database_url)
        self._engine: Engine = create_engine(self._database_url, pool_pre_ping=True)

    def add_run_outcome(self, payload: RunSummary) -> None:
        """Persist one run summary and all source-scoped outcomes."""
        run_id = str(payload["run_id"])
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO ingestion_runs (
                        id,
                        run_id,
                        trigger_type,
                        lifecycle_state,
                        outcome_state,
                        started_at,
                        completed_at,
                        accepted_count,
                        quarantined_count,
                        failed_count,
                        duplicate_no_op_count,
                        conflict_count
                    ) VALUES (
                        :id,
                        :run_id,
                        :trigger_type,
                        :lifecycle_state,
                        :outcome_state,
                        :started_at,
                        :completed_at,
                        :accepted_count,
                        :quarantined_count,
                        :failed_count,
                        :duplicate_no_op_count,
                        :conflict_count
                    )
                    ON CONFLICT (run_id) DO UPDATE
                    SET
                        trigger_type = EXCLUDED.trigger_type,
                        lifecycle_state = EXCLUDED.lifecycle_state,
                        outcome_state = EXCLUDED.outcome_state,
                        started_at = EXCLUDED.started_at,
                        completed_at = EXCLUDED.completed_at,
                        accepted_count = EXCLUDED.accepted_count,
                        quarantined_count = EXCLUDED.quarantined_count,
                        failed_count = EXCLUDED.failed_count,
                        duplicate_no_op_count = EXCLUDED.duplicate_no_op_count,
                        conflict_count = EXCLUDED.conflict_count
                    """
                ),
                {
                    "id": uuid4(),
                    "run_id": run_id,
                    "trigger_type": str(payload["trigger_type"]),
                    "lifecycle_state": "completed",
                    "outcome_state": str(payload["outcome_state"]),
                    "started_at": self._as_datetime(payload["started_at"]),
                    "completed_at": self._as_datetime(payload["completed_at"]),
                    "accepted_count": int(payload["accepted_count"]),
                    "quarantined_count": int(payload["quarantined_count"]),
                    "failed_count": int(payload["failed_count"]),
                    "duplicate_no_op_count": int(payload["duplicate_no_op_count"]),
                    "conflict_count": int(payload["conflict_count"]),
                },
            )

            for source_result in payload["source_results"]:
                connection.execute(
                    text(
                        """
                        INSERT INTO source_run_outcomes (
                            id,
                            run_id,
                            source_key,
                            state,
                            accepted_count,
                            quarantined_count,
                            failed_count,
                            duplicate_no_op_count,
                            conflict_count,
                            message
                        ) VALUES (
                            :id,
                            :run_id,
                            :source_key,
                            :state,
                            :accepted_count,
                            :quarantined_count,
                            :failed_count,
                            :duplicate_no_op_count,
                            :conflict_count,
                            :message
                        )
                        ON CONFLICT (run_id, source_key) DO UPDATE
                        SET
                            state = EXCLUDED.state,
                            accepted_count = EXCLUDED.accepted_count,
                            quarantined_count = EXCLUDED.quarantined_count,
                            failed_count = EXCLUDED.failed_count,
                            duplicate_no_op_count = EXCLUDED.duplicate_no_op_count,
                            conflict_count = EXCLUDED.conflict_count,
                            message = EXCLUDED.message
                        """
                    ),
                    {
                        "id": uuid4(),
                        "run_id": run_id,
                        "source_key": str(source_result["source_key"]),
                        "state": str(source_result["status"]),
                        "accepted_count": self._as_int(
                            source_result.get("accepted_count", 0)
                        ),
                        "quarantined_count": self._as_int(
                            source_result.get("quarantined_count", 0)
                        ),
                        "failed_count": self._as_int(source_result.get("failed_count", 0)),
                        "duplicate_no_op_count": self._as_int(
                            source_result.get("duplicate_no_op_count", 0)
                        ),
                        "conflict_count": self._as_int(source_result.get("conflict_count", 0)),
                        "message": source_result.get("message"),
                    },
                )

    @staticmethod
    def _as_datetime(value: object) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        raise TypeError("payload datetime fields must be datetime or ISO8601 strings")

    @staticmethod
    def _as_int(value: object) -> int:
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            return int(value)
        return 0

    def fetch_run(self, run_id: str) -> dict[str, Any] | None:
        """Fetch persisted run and source outcomes for verification workflows."""
        with self._engine.begin() as connection:
            run_row = connection.execute(
                text(
                    """
                    SELECT
                        run_id,
                        trigger_type,
                        lifecycle_state,
                        outcome_state,
                        accepted_count,
                        quarantined_count,
                        failed_count,
                        duplicate_no_op_count,
                        conflict_count
                    FROM ingestion_runs
                    WHERE run_id = :run_id
                    """
                ),
                {"run_id": run_id},
            ).mappings().first()
            if run_row is None:
                return None

            outcome_rows = connection.execute(
                text(
                    """
                    SELECT
                        source_key,
                        state,
                        accepted_count,
                        quarantined_count,
                        failed_count,
                        duplicate_no_op_count,
                        conflict_count,
                        message
                    FROM source_run_outcomes
                    WHERE run_id = :run_id
                    ORDER BY source_key ASC
                    """
                ),
                {"run_id": run_id},
            ).mappings().all()

        return {
            "run": dict(run_row),
            "outcomes": [dict(row) for row in outcome_rows],
        }

    def clear_run(self, run_id: str) -> None:
        """Delete persisted run and source outcomes by run id for test cleanup."""
        with self._engine.begin() as connection:
            connection.execute(
                text("DELETE FROM source_run_outcomes WHERE run_id = :run_id"),
                {"run_id": run_id},
            )
            connection.execute(
                text("DELETE FROM ingestion_runs WHERE run_id = :run_id"),
                {"run_id": run_id},
            )

    def clear_all(self) -> None:
        """Delete all persisted runtime rows for local integration checks."""
        with self._engine.begin() as connection:
            connection.execute(text("DELETE FROM source_run_outcomes"))
            connection.execute(text("DELETE FROM ingestion_runs"))
