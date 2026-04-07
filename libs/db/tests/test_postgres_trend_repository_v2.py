"""V2 repository contract tests for trend descriptor persistence plumbing."""

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
        return _FakeResult(scalar_value=1)


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


def test_upsert_lookback_snapshot_accepts_v2_fields(monkeypatch) -> None:
    """Repository should include v2 columns in lookback snapshot upsert SQL."""

    fake_connection = _FakeConnection()
    fake_engine = _FakeEngine(fake_connection)

    monkeypatch.setattr(
        "db.repositories.postgres_trend_repository.create_engine",
        lambda *_args, **_kwargs: fake_engine,
    )

    repository = PostgresTrendRepository(database_url="postgresql+psycopg://unused")
    repository.upsert_lookback_snapshot(
        {
            "series_key": "SERIES.KEY",
            "observed_on": "2026-03-01",
            "observation_id": None,
            "lookback_points": 25,
            "outcome_state": "significant_trend",
            "descriptor_state": "available",
            "trend_label": "moderate_uptrend",
            "direction": "up",
            "confidence_score": 0.7,
            "dominant_measure_family": "theil_sen",
            "theil_sen_slope": 1.2,
            "theil_sen_low_slope": 0.8,
            "theil_sen_high_slope": 1.5,
            "kendall_tau": 0.5,
            "kendall_pvalue": 0.01,
            "ols_slope": 1.1,
            "ols_intercept": 97.0,
            "ols_r_squared": 0.6,
            "ols_pvalue": 0.02,
            "preprocessing": {"smoothing_method": "ewma"},
            "reason_code": None,
            "strength": None,
            "seasonality_classification": None,
            "analysis_version": "v2",
        }
    )

    assert any("descriptor_state" in sql for sql, _ in fake_connection.executed)
    assert any("confidence_score" in sql for sql, _ in fake_connection.executed)
