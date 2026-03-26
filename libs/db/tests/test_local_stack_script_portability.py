"""Compose-first local-stack contract checks."""

from __future__ import annotations

from pathlib import Path


def test_compose_declares_dual_database_services_with_healthchecks() -> None:
    """Compose should own readiness for both canonical and metadata databases."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "db:" in compose
    assert "dagster_db:" in compose
    assert "pg_isready" in compose


def test_backend_compose_service_owns_shared_db_migrations() -> None:
    """Shared DB migrations should be applied by backend startup, not wrapper scripts."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "alembic -c libs/db/alembic.ini upgrade head" in compose
    assert "python -m src.http_api_server" in compose
