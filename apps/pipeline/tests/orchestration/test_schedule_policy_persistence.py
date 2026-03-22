"""Integration tests for persisted source schedule policy state."""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.definitions import get_ingest_runtime
from src.orchestration.runtime import IngestRuntime


def _get_runtime_or_skip() -> IngestRuntime:
    runtime = get_ingest_runtime()
    run_repo = runtime.run_repository

    probe_run_id = f"schedule-probe-{uuid4()}"
    try:
        run_repo.fetch_run(probe_run_id)
    except Exception as exc:  # pragma: no cover - environment-dependent integration guard
        pytest.skip(f"postgres runtime DB unavailable for integration test: {exc}")
    return runtime


def test_read_all_schedule_policies_returns_empty_when_table_has_no_rows() -> None:
    """Repository should return an empty mapping when no schedule rows exist."""
    runtime = _get_runtime_or_skip()
    run_repo = runtime.run_repository

    run_repo.clear_all()

    assert run_repo.read_all_schedule_policies() == {}


def test_read_all_schedule_policies_returns_all_inserted_rows() -> None:
    """Repository should return all persisted rows keyed by source key."""
    runtime = _get_runtime_or_skip()
    run_repo = runtime.run_repository

    run_repo.clear_all()
    now = datetime.now(tz=UTC)
    run_repo.upsert_schedule_policy(
        source_key="source-a",
        cadence_type="hourly",
        last_successful_at=now,
        updated_at=now,
    )
    run_repo.upsert_schedule_policy(
        source_key="source-b",
        cadence_type="daily",
        last_successful_at=now - timedelta(days=1),
        updated_at=now,
    )

    rows = run_repo.read_all_schedule_policies()

    assert set(rows.keys()) == {"source-a", "source-b"}
    assert rows["source-a"]["cadence_type"] == "hourly"
    assert rows["source-b"]["cadence_type"] == "daily"


def test_upsert_schedule_policy_inserts_new_row_for_new_source_key() -> None:
    """Upsert should insert a row when source key does not already exist."""
    runtime = _get_runtime_or_skip()
    run_repo = runtime.run_repository

    run_repo.clear_all()
    now = datetime.now(tz=UTC)
    run_repo.upsert_schedule_policy(
        source_key="source-new",
        cadence_type="weekly",
        last_successful_at=now,
        updated_at=now,
    )

    rows = run_repo.read_all_schedule_policies()

    assert "source-new" in rows
    assert rows["source-new"]["cadence_type"] == "weekly"
    assert rows["source-new"]["last_successful_at"] is not None


def test_upsert_schedule_policy_overwrites_last_successful_at_on_conflict() -> None:
    """Upsert should update persisted timestamp for an existing source key."""
    runtime = _get_runtime_or_skip()
    run_repo = runtime.run_repository

    run_repo.clear_all()
    earlier = datetime.now(tz=UTC) - timedelta(days=3)
    later = datetime.now(tz=UTC)

    run_repo.upsert_schedule_policy(
        source_key="source-update",
        cadence_type="daily",
        last_successful_at=earlier,
        updated_at=earlier,
    )
    run_repo.upsert_schedule_policy(
        source_key="source-update",
        cadence_type="daily",
        last_successful_at=later,
        updated_at=later,
    )

    row = run_repo.read_all_schedule_policies()["source-update"]

    assert row["last_successful_at"] == later


def test_clear_all_removes_source_schedule_policies_rows() -> None:
    """Full repository cleanup should include source schedule policy rows."""
    runtime = _get_runtime_or_skip()
    run_repo = runtime.run_repository

    run_repo.clear_all()
    now = datetime.now(tz=UTC)
    run_repo.upsert_schedule_policy(
        source_key="source-clear",
        cadence_type="hourly",
        last_successful_at=now,
        updated_at=now,
    )

    run_repo.clear_all()

    with run_repo._engine.begin() as connection:  # noqa: SLF001 - integration assertion only
        count = connection.execute(
            text("SELECT COUNT(*) FROM source_schedule_policies")
        ).scalar_one()

    assert int(count) == 0
