"""US3 backend regressions for local DB setup defects."""

from pathlib import Path


def test_compose_uses_non_conflicting_local_db_port_default() -> None:
    """Verify compose default host port avoids common local Postgres conflicts."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert '"${LOCAL_DB_PORT:-55432}:5432"' in compose


def test_migration_runner_auto_starts_db_service() -> None:
    """Verify migration helper can bootstrap DB service automatically."""
    script = Path("tools/quality/local-stack/run-db-migrations.sh").read_text(encoding="utf-8")
    assert "docker compose up -d db" in script
    assert "DB service is not healthy" in script
