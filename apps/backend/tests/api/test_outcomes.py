"""Tests for GET /api/runs/{run_id}/outcomes endpoint."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.app import create_app
from src.api.dependencies import get_db_session
from tests.conftest import make_outcome, make_run


def _client(session: Session) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_db_session] = lambda: session
    return TestClient(app, raise_server_exceptions=False)


def test_list_outcomes_returns_200_empty(db_session: Session) -> None:
    """GET /api/runs/{run_id}/outcomes returns empty list when run has no outcomes."""
    run = make_run(run_id="run-001")
    db_session.add(run)
    db_session.flush()

    response = _client(db_session).get("/api/runs/run-001/outcomes")
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0


def test_list_outcomes_returns_seeded_outcomes(db_session: Session) -> None:
    """GET /api/runs/{run_id}/outcomes returns all outcomes for the run."""
    run = make_run(run_id="run-001")
    o1 = make_outcome("run-001", source_key="src.a", state="success")
    o2 = make_outcome("run-001", source_key="src.b", state="failure")
    db_session.add_all([run, o1, o2])
    db_session.flush()

    response = _client(db_session).get("/api/runs/run-001/outcomes")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    states = {item["state"] for item in body["items"]}
    assert states == {"success", "failure"}


def test_list_outcomes_returns_all_stable_state_values(db_session: Session) -> None:
    """Outcomes with each valid state value are returned correctly."""
    run = make_run(run_id="run-multi")
    for state in ("success", "partial_success", "failure", "not_due", "deferred", "conflict"):
        db_session.add(make_outcome("run-multi", source_key=f"src.{state}", state=state))
    db_session.add(run)
    db_session.flush()

    response = _client(db_session).get("/api/runs/run-multi/outcomes")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 6


def test_list_outcomes_returns_404_for_unknown_run(db_session: Session) -> None:
    """GET /api/runs/{run_id}/outcomes returns 404 when run does not exist."""
    response = _client(db_session).get("/api/runs/no-such-run/outcomes")
    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "not_found"
