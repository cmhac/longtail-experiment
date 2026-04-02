"""Contract checks for repeatable compose migration behavior."""

from __future__ import annotations

from pathlib import Path


def test_backend_compose_runner_uses_non_destructive_upgrade_head() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "upgrade head" in compose
    assert "downgrade" not in compose


def test_revision_check_guidance_is_deterministic() -> None:
    agents_md = Path("AGENTS.md").read_text(encoding="utf-8")
    assert "0012_lookback_trend_snapshots" in agents_md
    assert "SELECT version_num FROM alembic_version;" in agents_md
