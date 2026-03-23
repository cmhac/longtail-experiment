"""Unit tests for EligibilityRepository."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session

from src.repositories.eligibility_repository import EligibilityRepository
from tests.conftest import make_eligibility, make_run


def test_list_eligibility_empty(db_session: Session) -> None:
    """list_eligibility_for_run returns empty list when no records exist."""
    run = make_run(run_id="run-001")
    db_session.add(run)
    db_session.flush()

    repo = EligibilityRepository()
    records, total = repo.list_eligibility_for_run(db_session, "run-001")
    assert records == []
    assert total == 0


def test_list_eligibility_returns_matching(db_session: Session) -> None:
    """list_eligibility_for_run returns only records for the specified run."""
    run1 = make_run(run_id="run-001")
    run2 = make_run(run_id="run-002")
    e1 = make_eligibility("run-001", source_key="src.a")
    e2 = make_eligibility("run-002", source_key="src.b")
    db_session.add_all([run1, run2, e1, e2])
    db_session.flush()

    repo = EligibilityRepository()
    records, total = repo.list_eligibility_for_run(db_session, "run-001")
    assert total == 1
    assert records[0].source_key == "src.a"
