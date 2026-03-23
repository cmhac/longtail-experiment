"""Tests for GET /api/runs and GET /api/runs/{run_id} endpoints."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.app import create_app
from src.api.dependencies import get_db_session
from tests.conftest import make_run


def _client(session: Session) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_db_session] = lambda: session
    return TestClient(app, raise_server_exceptions=False)


def test_list_runs_returns_200_with_empty_db(db_session: Session) -> None:
    """GET /api/runs returns 200 with empty items when no runs exist."""
    response = _client(db_session).get("/api/runs")
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["page"] == 1


def test_list_runs_returns_seeded_runs(db_session: Session) -> None:
    """GET /api/runs returns seeded runs in descending order."""
    r1 = make_run(run_id="run-001", started_at=datetime(2024, 1, 1, tzinfo=UTC))
    r2 = make_run(run_id="run-002", started_at=datetime(2024, 2, 1, tzinfo=UTC))
    db_session.add_all([r1, r2])
    db_session.flush()

    response = _client(db_session).get("/api/runs")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    # Descending order: run-002 first
    assert body["items"][0]["run_id"] == "run-002"
    assert body["items"][1]["run_id"] == "run-001"


def test_list_runs_pagination(db_session: Session) -> None:
    """GET /api/runs respects page and page_size parameters."""
    for _ in range(5):
        db_session.add(make_run())
    db_session.flush()

    response = _client(db_session).get("/api/runs?page=1&page_size=2")
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert len(body["items"]) == 2
    assert body["total"] == 5


def test_list_runs_invalid_page_returns_422(db_session: Session) -> None:
    """GET /api/runs returns 422 when page < 1."""
    response = _client(db_session).get("/api/runs?page=0")
    assert response.status_code == 422
    body = response.json()
    assert "code" in body


def test_list_runs_invalid_page_size_returns_422(db_session: Session) -> None:
    """GET /api/runs returns 422 when page_size > 200."""
    response = _client(db_session).get("/api/runs?page_size=201")
    assert response.status_code == 422


def test_get_run_returns_200_for_existing_run(db_session: Session) -> None:
    """GET /api/runs/{run_id} returns 200 with full detail for existing run."""
    run = make_run(run_id="run-xyz")
    db_session.add(run)
    db_session.flush()

    response = _client(db_session).get("/api/runs/run-xyz")
    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] == "run-xyz"
    assert "trigger_type" in body
    assert "lifecycle_state" in body
    assert "outcome_state" in body
    assert "started_at" in body


def test_get_run_returns_404_for_unknown_run(db_session: Session) -> None:
    """GET /api/runs/{run_id} returns 404 with error envelope for unknown run_id."""
    response = _client(db_session).get("/api/runs/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "not_found"
    assert "message" in body
