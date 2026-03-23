"""Tests for GET /health endpoint."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from sqlalchemy.exc import OperationalError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient

from src.api.app import create_app


def _client() -> TestClient:
    return TestClient(create_app(), raise_server_exceptions=False)


def test_health_returns_200_when_db_reachable() -> None:
    """GET /health returns 200 with status=ok when DB probe succeeds."""
    with patch("src.api.routers.health.create_db_engine") as mock_engine_factory:
        mock_conn = MagicMock()
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__ = lambda s: mock_conn
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_engine_factory.return_value = mock_engine

        response = _client().get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["db"] == "reachable"


def test_health_returns_503_when_db_unreachable() -> None:
    """GET /health returns 503 with structured error body when DB is unavailable."""
    with patch("src.api.routers.health.create_db_engine") as mock_engine_factory:
        mock_engine = MagicMock()
        exc = OperationalError.__new__(OperationalError)
        exc.args = ("connection refused",)
        mock_engine.connect.side_effect = exc
        mock_engine_factory.return_value = mock_engine

        response = _client().get("/health")

    assert response.status_code == 503
    body = response.json()
    assert body["code"] == "service_unavailable"
    assert "message" in body


def test_health_response_has_db_field() -> None:
    """GET /health response always includes a db field."""
    with patch("src.api.routers.health.create_db_engine") as mock_engine_factory:
        mock_conn = MagicMock()
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__ = lambda s: mock_conn
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_engine_factory.return_value = mock_engine

        response = _client().get("/health")

    assert "db" in response.json()
