"""US2 contract tests for compose-owned migration behavior."""

from __future__ import annotations

from pathlib import Path


def test_backend_compose_command_runs_migrations_before_api_startup() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "alembic -c libs/db/alembic.ini upgrade head" in compose
    assert "python -m src.http_api_server" in compose


def test_docs_point_recovery_toward_compose_commands() -> None:
    runbook = Path("docs/runbooks/local-stack-baseline.md").read_text(encoding="utf-8")

    assert "docker compose up -d backend" in runbook
    assert "docker compose exec db psql" in runbook
