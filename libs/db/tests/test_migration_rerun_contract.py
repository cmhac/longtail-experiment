"""Contract checks for repeatable compose migration behavior."""

from __future__ import annotations

from pathlib import Path


def test_backend_compose_runner_uses_non_destructive_upgrade_head() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "upgrade head" in compose
    assert "downgrade" not in compose


def test_revision_check_guidance_uses_dynamic_alembic_head() -> None:
    agents_md = Path("AGENTS.md").read_text(encoding="utf-8")
    assert "current Alembic head" in agents_md
    assert "libs/db/alembic.ini" in agents_md
    assert "do not pin a fixed revision in compose" in agents_md
    assert "SELECT version_num FROM alembic_version;" in agents_md
