"""US3 backend regressions for local DB setup defects."""

from pathlib import Path


def test_compose_uses_non_conflicting_local_db_port_default() -> None:
    """Verify compose default host port avoids common local Postgres conflicts."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert '"${LOCAL_DB_PORT:-55432}:5432"' in compose


def test_backend_service_owns_db_migration_startup() -> None:
    """Verify backend startup is the compose migration entry point."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "uv run --project apps/backend alembic -c libs/db/alembic.ini upgrade head" in compose
    assert "depends_on:" in compose
