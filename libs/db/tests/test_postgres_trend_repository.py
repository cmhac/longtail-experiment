"""Unit tests for Postgres trend repository SQL operation wiring."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from db.repositories.postgres_trend_repository import PostgresTrendRepository


class _FakeResult:
    def __init__(self, *, scalar_value: object) -> None:
        self._scalar_value = scalar_value

    def scalar_one(self) -> object:
        return self._scalar_value


class _FakeConnection:
    def __init__(self) -> None:
        self.executed: list[tuple[str, dict[str, object]]] = []

    def execute(self, statement, params):
        self.executed.append((str(statement), dict(params)))
        sql = str(statement)
        if "RETURNING id" in sql:
            return _FakeResult(scalar_value="00000000-0000-0000-0000-000000000001")
        return _FakeResult(scalar_value=3)


class _FakeBeginContext:
    def __init__(self, connection: _FakeConnection) -> None:
        self._connection = connection

    def __enter__(self) -> _FakeConnection:
        return self._connection

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class _FakeEngine:
    def __init__(self, connection: _FakeConnection) -> None:
        self._connection = connection

    def begin(self) -> _FakeBeginContext:
        return _FakeBeginContext(self._connection)


def test_upsert_trend_record_executes_insert_sql(monkeypatch) -> None:
    """Repository should execute trend-record insert and return canonical id."""

    fake_connection = _FakeConnection()
    fake_engine = _FakeEngine(fake_connection)

    monkeypatch.setattr(
        "db.repositories.postgres_trend_repository.create_engine",
        lambda *_args, **_kwargs: fake_engine,
    )

    repository = PostgresTrendRepository(database_url="postgresql+psycopg://unused")
    record_id = repository.upsert_trend_record(
        {
            "series_key": "SERIES.KEY",
            "trend_label": "mild_sustained_uptrend",
            "direction": "up",
            "strength": "mild",
            "seasonality_classification": "non_seasonal",
            "start_period": "2026-01-01T00:00:00+00:00",
            "end_period": None,
            "is_ongoing": True,
        }
    )

    assert record_id == "00000000-0000-0000-0000-000000000001"
    assert any(
        "INSERT INTO trend_records" in sql for sql, _ in fake_connection.executed
    )


def test_append_transition_executes_insert_sql(monkeypatch) -> None:
    """Repository should append transition rows with expected transition type."""

    fake_connection = _FakeConnection()
    fake_engine = _FakeEngine(fake_connection)

    monkeypatch.setattr(
        "db.repositories.postgres_trend_repository.create_engine",
        lambda *_args, **_kwargs: fake_engine,
    )

    repository = PostgresTrendRepository(database_url="postgresql+psycopg://unused")
    repository.append_transition(
        {
            "series_key": "SERIES.KEY",
            "transition_type": "created",
            "prior_trend_record_id": None,
            "new_trend_record_id": "00000000-0000-0000-0000-000000000001",
            "trigger_observation_on": "2026-02-01T00:00:00+00:00",
            "reason": "first_significant_trend",
        }
    )

    assert any(
        "INSERT INTO trend_transition_events" in sql
        for sql, _ in fake_connection.executed
    )


def test_count_trend_records_for_series_reads_scalar_count(monkeypatch) -> None:
    """Repository should return integer count for one series key."""

    fake_connection = _FakeConnection()
    fake_engine = _FakeEngine(fake_connection)

    monkeypatch.setattr(
        "db.repositories.postgres_trend_repository.create_engine",
        lambda *_args, **_kwargs: fake_engine,
    )

    repository = PostgresTrendRepository(database_url="postgresql+psycopg://unused")
    count = repository.count_trend_records_for_series(series_key="SERIES.KEY")

    assert count == 3
    assert any("SELECT COUNT(*)" in sql for sql, _ in fake_connection.executed)


def test_count_canonical_descriptors_for_series_reads_scalar_count(monkeypatch) -> None:
    """Repository should return canonical descriptor count for one series key."""

    fake_connection = _FakeConnection()
    fake_engine = _FakeEngine(fake_connection)

    monkeypatch.setattr(
        "db.repositories.postgres_trend_repository.create_engine",
        lambda *_args, **_kwargs: fake_engine,
    )

    repository = PostgresTrendRepository(database_url="postgresql+psycopg://unused")
    count = repository.count_canonical_descriptors_for_series(series_key="SERIES.KEY")

    assert count == 3
    assert any(
        "FROM trend_canonical_descriptors" in sql for sql, _ in fake_connection.executed
    )
