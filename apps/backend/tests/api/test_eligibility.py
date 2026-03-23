"""Tests for GET /api/runs/{run_id}/eligibility endpoint."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.app import create_app
from src.api.dependencies import get_db_session
from tests.conftest import make_eligibility, make_run


def _client(session: Session) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_db_session] = lambda: session
    return TestClient(app, raise_server_exceptions=False)


def test_list_eligibility_returns_200_empty(db_session: Session) -> None:
    """GET /api/runs/{run_id}/eligibility returns empty list when no records exist."""
    run = make_run(run_id="run-001")
    db_session.add(run)
    db_session.flush()

    response = _client(db_session).get("/api/runs/run-001/eligibility")
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0


def test_list_eligibility_returns_seeded_records(db_session: Session) -> None:
    """GET /api/runs/{run_id}/eligibility returns all eligibility records for the run."""
    run = make_run(run_id="run-001")
    e1 = make_eligibility("run-001", source_key="src.a")
    e2 = make_eligibility("run-001", source_key="src.b")
    db_session.add_all([run, e1, e2])
    db_session.flush()

    response = _client(db_session).get("/api/runs/run-001/eligibility")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    source_keys = {item["source_key"] for item in body["items"]}
    assert source_keys == {"src.a", "src.b"}


def test_list_eligibility_returns_correct_field_names(db_session: Session) -> None:
    """GET /api/runs/{run_id}/eligibility response includes eligibility_state and reason_code."""
    run = make_run(run_id="run-001")
    e = make_eligibility("run-001")
    db_session.add_all([run, e])
    db_session.flush()

    response = _client(db_session).get("/api/runs/run-001/eligibility")
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert "eligibility_state" in item
    assert "reason_code" in item
    assert "selected_for_execution" in item
    assert "evaluated_at" in item


def test_list_eligibility_returns_404_for_unknown_run(db_session: Session) -> None:
    """GET /api/runs/{run_id}/eligibility returns 404 for unknown run_id."""
    response = _client(db_session).get("/api/runs/no-such-run/eligibility")
    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "not_found"
