"""Unit tests for ConflictRepository."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session

from src.repositories.conflict_repository import ConflictRepository
from tests.conftest import make_conflict, make_run


def test_list_conflicts_empty(db_session: Session) -> None:
    """list_conflicts returns empty list when no conflicts exist."""
    repo = ConflictRepository()
    conflicts, total = repo.list_conflicts(db_session)
    assert conflicts == []
    assert total == 0


def test_list_conflicts_no_filters(db_session: Session) -> None:
    """list_conflicts with no filters returns all conflicts."""
    run = make_run(run_id="run-001")
    c1 = make_conflict("run-001", conflict_state="open")
    c2 = make_conflict("run-001", conflict_state="resolved")
    db_session.add_all([run, c1, c2])
    db_session.flush()

    repo = ConflictRepository()
    conflicts, total = repo.list_conflicts(db_session)
    assert total == 2


def test_list_conflicts_filter_by_run_id(db_session: Session) -> None:
    """list_conflicts with run_id filter returns only matching conflicts."""
    r1 = make_run(run_id="run-001")
    r2 = make_run(run_id="run-002")
    c1 = make_conflict("run-001")
    c2 = make_conflict("run-002")
    db_session.add_all([r1, r2, c1, c2])
    db_session.flush()

    repo = ConflictRepository()
    conflicts, total = repo.list_conflicts(db_session, run_id="run-001")
    assert total == 1
    assert conflicts[0].run_id == "run-001"


def test_list_conflicts_filter_by_conflict_state(db_session: Session) -> None:
    """list_conflicts with conflict_state filter returns only matching conflicts."""
    run = make_run(run_id="run-001")
    c_open = make_conflict("run-001", conflict_state="open")
    c_suppressed = make_conflict("run-001", conflict_state="suppressed")
    db_session.add_all([run, c_open, c_suppressed])
    db_session.flush()

    repo = ConflictRepository()
    conflicts, total = repo.list_conflicts(db_session, conflict_state="open")
    assert total == 1
    assert conflicts[0].conflict_state == "open"


def test_list_conflicts_invalid_conflict_state_raises(db_session: Session) -> None:
    """list_conflicts raises ValueError for invalid conflict_state."""
    repo = ConflictRepository()
    with pytest.raises(ValueError, match="conflict_state must be one of"):
        repo.list_conflicts(db_session, conflict_state="invalid")


def test_list_conflicts_no_match_returns_empty(db_session: Session) -> None:
    """list_conflicts returns empty list when filter matches no records."""
    run = make_run(run_id="run-001")
    db_session.add_all([run, make_conflict("run-001")])
    db_session.flush()

    repo = ConflictRepository()
    conflicts, total = repo.list_conflicts(db_session, run_id="nonexistent")
    assert total == 0
    assert conflicts == []
