"""Foundational migration readiness contract tests."""

from __future__ import annotations

from pathlib import Path


def test_alembic_ini_config_exists_with_script_location() -> None:
    alembic_ini = Path("libs/db/alembic.ini")
    assert alembic_ini.exists()
    content = alembic_ini.read_text(encoding="utf-8")
    assert "script_location = libs/db/alembic" in content


def test_migration_command_contracts_present_in_compose_and_docs() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    quickstart = Path("specs/004-local-dev-db/quickstart.md").read_text(
        encoding="utf-8"
    )

    assert "alembic -c libs/db/alembic.ini upgrade head" in compose
    assert "docker compose exec db psql" in quickstart
