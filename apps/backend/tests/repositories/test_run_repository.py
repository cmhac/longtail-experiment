"""Unit tests for RunRepository."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session

from src.repositories.run_repository import RunRepository
from tests.conftest import make_run


def test_list_runs_empty(db_session: Session) -> None:
    """list_runs returns empty list when no runs exist."""
    repo = RunRepository()
    runs, total = repo.list_runs(db_session)
    assert runs == []
    assert total == 0


def test_list_runs_returns_all(db_session: Session) -> None:
    """list_runs returns all runs."""
    db_session.add_all([make_run(), make_run(), make_run()])
    db_session.flush()

    repo = RunRepository()
    runs, total = repo.list_runs(db_session)
    assert total == 3
    assert len(runs) == 3


def test_list_runs_ordered_descending(db_session: Session) -> None:
    """list_runs returns runs ordered by started_at descending."""
    r_old = make_run(run_id="old", started_at=datetime(2024, 1, 1, tzinfo=UTC))
    r_new = make_run(run_id="new", started_at=datetime(2024, 6, 1, tzinfo=UTC))
    db_session.add_all([r_old, r_new])
    db_session.flush()

    repo = RunRepository()
    runs, total = repo.list_runs(db_session)
    assert runs[0].run_id == "new"
    assert runs[1].run_id == "old"


def test_list_runs_pagination(db_session: Session) -> None:
    """list_runs respects page and page_size parameters."""
    for _ in range(5):
        db_session.add(make_run())
    db_session.flush()

    repo = RunRepository()
    runs, total = repo.list_runs(db_session, page=1, page_size=2)
    assert total == 5
    assert len(runs) == 2


def test_get_run_by_run_id_found(db_session: Session) -> None:
    """get_run_by_run_id returns the run when it exists."""
    run = make_run(run_id="run-found")
    db_session.add(run)
    db_session.flush()

    repo = RunRepository()
    result = repo.get_run_by_run_id(db_session, "run-found")
    assert result is not None
    assert result.run_id == "run-found"


def test_get_run_by_run_id_not_found(db_session: Session) -> None:
    """get_run_by_run_id returns None when run does not exist."""
    repo = RunRepository()
    result = repo.get_run_by_run_id(db_session, "nonexistent")
    assert result is None
