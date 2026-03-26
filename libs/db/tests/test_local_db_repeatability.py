"""US3 repeatability checks for compose-based local DB workflows."""

from __future__ import annotations

from pathlib import Path


def test_compose_migration_guidance_avoids_destructive_reset_steps() -> None:
    agents_md = Path("AGENTS.md").read_text(encoding="utf-8")
    assert "docker compose down -v" not in agents_md


def test_compose_declares_db_healthchecks() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert '"Health":"healthy"' not in compose
    assert "healthcheck:" in compose
    assert "pg_isready" in compose
