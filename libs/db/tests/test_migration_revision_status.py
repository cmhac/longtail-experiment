"""US2 tests for migration revision status guidance."""

from __future__ import annotations

from pathlib import Path


def test_revision_check_uses_dynamic_baseline_default() -> None:
    agents_md = Path("AGENTS.md").read_text(encoding="utf-8")
    assert "Runtime schema readiness expects the current Alembic head" in agents_md
    assert "do not pin a fixed revision in compose" in agents_md


def test_revision_check_uses_compose_db_query() -> None:
    quickstart = Path("specs/004-local-dev-db/quickstart.md").read_text(
        encoding="utf-8"
    )
    assert "expected latest shared-db revision" in quickstart
    assert "docker compose exec db psql" in quickstart
    assert "SELECT version_num FROM alembic_version;" in quickstart
