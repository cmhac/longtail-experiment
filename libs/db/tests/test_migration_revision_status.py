"""US2 tests for migration revision status guidance."""

from __future__ import annotations

from pathlib import Path


def test_revision_check_uses_expected_baseline_default() -> None:
    agents_md = Path("AGENTS.md").read_text(encoding="utf-8")
    assert "Current migration head expected by local revision checks" in agents_md
    assert "0010_source_profile_metadata" in agents_md


def test_revision_check_uses_compose_db_query() -> None:
    quickstart = Path("specs/004-local-dev-db/quickstart.md").read_text(
        encoding="utf-8"
    )
    assert "docker compose exec db psql" in quickstart
    assert "SELECT version_num FROM alembic_version;" in quickstart
