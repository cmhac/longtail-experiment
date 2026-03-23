"""Tests for GET /api/conflicts endpoint."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.app import create_app
from src.api.dependencies import get_db_session
from tests.conftest import make_conflict, make_run


def _client(session: Session) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_db_session] = lambda: session
    return TestClient(app, raise_server_exceptions=False)


def test_list_conflicts_returns_200_empty(db_session: Session) -> None:
    """GET /api/conflicts returns 200 with empty list when no conflicts exist."""
    response = _client(db_session).get("/api/conflicts")
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0


def test_list_conflicts_returns_all_conflicts(db_session: Session) -> None:
    """GET /api/conflicts returns all conflicts when no filters are applied."""
    run = make_run(run_id="run-001")
    c1 = make_conflict("run-001", conflict_state="open")
    c2 = make_conflict("run-001", conflict_state="resolved")
    db_session.add_all([run, c1, c2])
    db_session.flush()

    response = _client(db_session).get("/api/conflicts")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2


def test_list_conflicts_filter_by_run_id(db_session: Session) -> None:
    """GET /api/conflicts?run_id= returns only matching conflicts."""
    r1 = make_run(run_id="run-001")
    r2 = make_run(run_id="run-002")
    c1 = make_conflict("run-001")
    c2 = make_conflict("run-002")
    db_session.add_all([r1, r2, c1, c2])
    db_session.flush()

    response = _client(db_session).get("/api/conflicts?run_id=run-001")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["run_id"] == "run-001"


def test_list_conflicts_filter_by_conflict_state(db_session: Session) -> None:
    """GET /api/conflicts?conflict_state= returns only matching conflicts."""
    run = make_run(run_id="run-001")
    c_open = make_conflict("run-001", conflict_state="open")
    c_resolved = make_conflict("run-001", conflict_state="resolved")
    db_session.add_all([run, c_open, c_resolved])
    db_session.flush()

    response = _client(db_session).get("/api/conflicts?conflict_state=open")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["conflict_state"] == "open"


def test_list_conflicts_invalid_conflict_state_returns_422(db_session: Session) -> None:
    """GET /api/conflicts?conflict_state=invalid returns 422 with error envelope."""
    response = _client(db_session).get("/api/conflicts?conflict_state=invalid_state")
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "validation_error"


def test_list_conflicts_empty_filter_returns_all(db_session: Session) -> None:
    """GET /api/conflicts with filter matching no records returns 200 with empty list."""
    run = make_run(run_id="run-001")
    db_session.add_all([run, make_conflict("run-001")])
    db_session.flush()

    response = _client(db_session).get("/api/conflicts?run_id=nonexistent")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["items"] == []


def test_list_conflicts_invalid_page_returns_422(db_session: Session) -> None:
    """GET /api/conflicts with page=0 returns 422."""
    response = _client(db_session).get("/api/conflicts?page=0")
    assert response.status_code == 422
