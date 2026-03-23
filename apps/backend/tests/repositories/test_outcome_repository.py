"""Unit tests for OutcomeRepository."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session

from src.repositories.outcome_repository import OutcomeRepository
from tests.conftest import make_outcome, make_run


def test_list_outcomes_empty(db_session: Session) -> None:
    """list_outcomes_for_run returns empty list when no outcomes exist for the run."""
    run = make_run(run_id="run-001")
    db_session.add(run)
    db_session.flush()

    repo = OutcomeRepository()
    outcomes, total = repo.list_outcomes_for_run(db_session, "run-001")
    assert outcomes == []
    assert total == 0


def test_list_outcomes_returns_matching(db_session: Session) -> None:
    """list_outcomes_for_run returns only outcomes for the specified run."""
    run1 = make_run(run_id="run-001")
    run2 = make_run(run_id="run-002")
    o1 = make_outcome("run-001", source_key="src.a")
    o2 = make_outcome("run-002", source_key="src.b")
    db_session.add_all([run1, run2, o1, o2])
    db_session.flush()

    repo = OutcomeRepository()
    outcomes, total = repo.list_outcomes_for_run(db_session, "run-001")
    assert total == 1
    assert outcomes[0].source_key == "src.a"
