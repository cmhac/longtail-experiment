"""Unit tests for PostgresRunRepository SQL mapping behavior using fake engine."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.resources import postgres_run_repository as repo_mod


class _FakeResult:
    def __init__(self, *, first_row=None, all_rows=None) -> None:
        self._first_row = first_row
        self._all_rows = all_rows or []

    def mappings(self):
        return self

    def first(self):
        return self._first_row

    def all(self):
        return self._all_rows


class _FakeBegin:
    def __init__(self, connection) -> None:
        self._connection = connection

    def __enter__(self):
        return self._connection

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class _FakeConnection:
    def __init__(self, *, scripted_results=None) -> None:
        self.calls: list[tuple[object, object]] = []
        self._scripted_results = list(scripted_results or [])

    def execute(self, statement, params=None):
        self.calls.append((statement, params))
        if self._scripted_results:
            return self._scripted_results.pop(0)
        return _FakeResult()


class _FakeEngine:
    def __init__(self, connection: _FakeConnection) -> None:
        self._connection = connection

    def begin(self):
        return _FakeBegin(self._connection)


def test_add_run_outcome_writes_source_and_series_outcomes(monkeypatch) -> None:
    """Run outcome persistence should write run, source, and series SQL statements."""
    connection = _FakeConnection()
    monkeypatch.setattr(repo_mod, "create_engine", lambda *args, **kwargs: _FakeEngine(connection))

    repository = repo_mod.PostgresRunRepository(database_url="postgresql+psycopg://x:y@z:5432/db")
    repository.add_run_outcome(
        {
            "run_id": "run-1",
            "trigger_type": "on_demand",
            "requested_by": "operator",
            "trigger_origin": "operator",
            "started_at": datetime.now(tz=UTC),
            "completed_at": datetime.now(tz=UTC),
            "source_results": [
                {
                    "source_key": "fred_fedfunds",
                    "status": "partial_success",
                    "accepted_count": 1,
                    "quarantined_count": 0,
                    "failed_count": 0,
                    "duplicate_no_op_count": 0,
                    "conflict_count": 0,
                    "outcome_reason_code": None,
                    "message": None,
                    "series_outcomes": [
                        {
                            "series_item_key": "fred_fedfunds",
                            "canonical_series_key": "INT.US.FEDFUNDS",
                            "provider_group_key": "fred",
                            "ownership_mode": "grouped",
                            "owner_adapter_key": "fred_fedfunds",
                            "status": "success",
                            "accepted_count": 1,
                            "quarantined_count": 0,
                            "failed_count": 0,
                        }
                    ],
                    "cadence_decisions": [
                        {
                            "series_key": "INT.US.FEDFUNDS",
                            "cadence_state": "regular",
                            "inferred_cadence": "daily",
                            "irregular_gap_count": 0,
                            "total_interval_count": 7,
                            "irregular_gap_ratio": 0.0,
                            "reason_code": "regular_spacing",
                            "reason_detail": None,
                        }
                    ],
                }
            ],
            "series_outcome_count": 1,
            "outcome_state": "partial_success",
            "accepted_count": 1,
            "quarantined_count": 0,
            "failed_count": 0,
            "failed_source_count": 0,
            "duplicate_no_op_count": 0,
            "conflict_count": 0,
            "due_source_count": 1,
            "executed_source_count": 1,
            "deferred_source_count": 0,
            "not_due_source_count": 0,
        }
    )

    sql_texts = [str(statement) for statement, _ in connection.calls]
    assert any("INSERT INTO ingestion_runs" in sql for sql in sql_texts)
    assert any("INSERT INTO source_run_outcomes" in sql for sql in sql_texts)
    assert any("INSERT INTO series_run_outcomes" in sql for sql in sql_texts)


def test_fetch_run_returns_run_outcomes_eligibility_and_series_rows(monkeypatch) -> None:
    """Fetch should return mapped run, source, eligibility, and series payload sections."""
    connection = _FakeConnection(
        scripted_results=[
            _FakeResult(first_row={"run_id": "run-1", "outcome_state": "success"}),
            _FakeResult(all_rows=[{"source_key": "fred_fedfunds", "state": "success"}]),
            _FakeResult(all_rows=[{"source_key": "fred_fedfunds", "eligibility_state": "due"}]),
            _FakeResult(
                all_rows=[
                    {
                        "source_key": "fred_fedfunds",
                        "series_item_key": "fred_fedfunds",
                        "ownership_mode": "grouped",
                    }
                ]
            ),
        ]
    )
    monkeypatch.setattr(repo_mod, "create_engine", lambda *args, **kwargs: _FakeEngine(connection))

    repository = repo_mod.PostgresRunRepository(database_url="postgresql+psycopg://x:y@z:5432/db")
    payload = repository.fetch_run("run-1")

    assert payload is not None
    assert payload["run"]["run_id"] == "run-1"
    assert payload["outcomes"][0]["source_key"] == "fred_fedfunds"
    assert payload["eligibility"][0]["source_key"] == "fred_fedfunds"
    assert payload["series_outcomes"][0]["series_item_key"] == "fred_fedfunds"


def test_fetch_run_returns_none_when_run_missing(monkeypatch) -> None:
    """Fetch should return None when no run row exists."""
    connection = _FakeConnection(scripted_results=[_FakeResult(first_row=None)])
    monkeypatch.setattr(repo_mod, "create_engine", lambda *args, **kwargs: _FakeEngine(connection))

    repository = repo_mod.PostgresRunRepository(database_url="postgresql+psycopg://x:y@z:5432/db")
    assert repository.fetch_run("missing") is None


def test_clear_operations_and_resolvers_execute_expected_paths(monkeypatch) -> None:
    """Clear and resolver helpers should execute cleanup and type-coercion branches."""
    connection = _FakeConnection()
    monkeypatch.setattr(repo_mod, "create_engine", lambda *args, **kwargs: _FakeEngine(connection))

    repository = repo_mod.PostgresRunRepository(database_url="postgresql+psycopg://x:y@z:5432/db")
    repository.clear_run("run-1")
    repository.clear_all()

    assert (
        repo_mod.resolve_database_url(
            explicit_url=None,
            environment={"DATABASE_URL": "postgresql://override"},
        )
        == "postgresql://override"
    )
    assert isinstance(repository.as_int("12"), int)
    assert isinstance(repository.as_datetime(datetime.now(tz=UTC)), datetime)


def test_eligibility_snapshot_write_and_read_paths(monkeypatch) -> None:
    """Eligibility snapshot write/read methods should handle empty and populated snapshots."""
    connection = _FakeConnection(
        scripted_results=[
            _FakeResult(),
            _FakeResult(
                all_rows=[
                    {
                        "source_key": "fred_fedfunds",
                        "eligibility_state": "due",
                        "reason_code": "scheduled_due",
                        "evaluated_at": datetime.now(tz=UTC),
                        "due_at": None,
                        "selected_for_execution": True,
                    }
                ]
            ),
        ]
    )
    monkeypatch.setattr(repo_mod, "create_engine", lambda *args, **kwargs: _FakeEngine(connection))

    repository = repo_mod.PostgresRunRepository(database_url="postgresql+psycopg://x:y@z:5432/db")
    repository.write_eligibility_snapshots(run_id="run-2", snapshots=[])
    repository.write_eligibility_snapshots(
        run_id="run-2",
        snapshots=[
            {
                "source_key": "fred_fedfunds",
                "eligibility_state": "due",
                "reason_code": "scheduled_due",
                "evaluated_at": datetime.now(tz=UTC),
                "due_at": None,
                "selected_for_execution": True,
            }
        ],
    )

    snapshots = repository.read_eligibility_snapshots("run-2")
    assert snapshots[0]["source_key"] == "fred_fedfunds"


def test_schedule_policy_read_and_upsert_paths(monkeypatch) -> None:
    """Schedule policy read and upsert methods should issue expected SQL operations."""
    connection = _FakeConnection(
        scripted_results=[
            _FakeResult(
                all_rows=[
                    {
                        "source_key": "fred_fedfunds",
                        "cadence_type": "daily",
                        "last_successful_at": datetime.now(tz=UTC),
                        "next_eligible_at": None,
                        "is_active": True,
                        "priority_class": "normal",
                    }
                ]
            )
        ]
    )
    monkeypatch.setattr(repo_mod, "create_engine", lambda *args, **kwargs: _FakeEngine(connection))

    repository = repo_mod.PostgresRunRepository(database_url="postgresql+psycopg://x:y@z:5432/db")
    rows = repository.read_all_schedule_policies()
    assert "fred_fedfunds" in rows

    repository.upsert_schedule_policy(
        source_key="fred_fedfunds",
        cadence_type="daily",
        last_successful_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
    )
    sql_texts = [str(statement) for statement, _ in connection.calls]
    assert any("INSERT INTO source_schedule_policies" in sql for sql in sql_texts)
