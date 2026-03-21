"""US1 checks for local DB bootstrap compose wiring."""

from pathlib import Path


def test_compose_contains_local_db_service_with_healthcheck() -> None:
    """Verify compose declares DB service image and health probe."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "db:" in compose
    assert "postgres:16-alpine" in compose
    assert "pg_isready" in compose


def test_compose_contains_persistent_volume_for_local_db() -> None:
    """Verify DB data volume is mounted for persistent local storage."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "local_db_data" in compose
    assert "local_db_data:/var/lib/postgresql/data" in compose
