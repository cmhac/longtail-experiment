"""Tests for the FastAPI app factory, dependency injection, and error handlers."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.api.app import create_app
from src.api.dependencies import get_db_session


def _make_client(session: Session | None = None) -> TestClient:
    """Create a TestClient with an optional DB session override."""
    app = create_app()
    if session is not None:
        app.dependency_overrides[get_db_session] = lambda: session
    return TestClient(app, raise_server_exceptions=False)


def test_app_factory_creates_app() -> None:
    """App factory returns a usable FastAPI application."""
    app = create_app()
    assert app is not None
    assert app.title == "Longtail Backend API"


def test_http_exception_returns_error_envelope() -> None:
    """HTTPExceptions are wrapped in the ErrorResponse envelope."""
    client = _make_client()
    # Hitting an unknown path gives a 404 from Starlette, not our handler,
    # but hitting a known route that raises HTTPException exercises the handler.
    response = client.get("/api/runs/nonexistent-run-id-xyz")
    # DB is not available in unit tests so we get a 503, which is fine.
    assert response.status_code in (404, 503)
    body = response.json()
    assert "code" in body
    assert "message" in body


def test_validation_error_returns_error_envelope() -> None:
    """RequestValidationError is wrapped in a structured ErrorResponse envelope."""
    client = _make_client()
    response = client.get("/api/runs?page=0")  # page < 1 → 422
    assert response.status_code == 422
    body = response.json()
    assert "code" in body
    assert "message" in body


def test_app_has_health_route() -> None:
    """The /health route is registered on the application."""
    app = create_app()
    routes = [route.path for route in app.routes]  # type: ignore[attr-defined]
    assert "/health" in routes


def test_app_has_api_runs_route() -> None:
    """The /api/runs route is registered on the application."""
    app = create_app()
    routes = [route.path for route in app.routes]  # type: ignore[attr-defined]
    assert "/api/runs" in routes


def test_app_has_conflicts_route() -> None:
    """The /api/conflicts route is registered on the application."""
    app = create_app()
    routes = [route.path for route in app.routes]  # type: ignore[attr-defined]
    assert "/api/conflicts" in routes
