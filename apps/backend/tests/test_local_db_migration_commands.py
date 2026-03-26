"""US2 backend-facing checks for compose migration command surfaces."""

from pathlib import Path


def test_quickstart_references_canonical_compose_migration_flow() -> None:
    """Verify quickstart points to compose-based migration commands."""
    quickstart = Path("specs/004-local-dev-db/quickstart.md").read_text(encoding="utf-8")
    assert "docker compose up -d backend" in quickstart
    assert "docker compose exec db psql" in quickstart


def test_backend_service_owns_migration_workflow() -> None:
    """Verify backend compose service is the migration entry point."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "alembic -c libs/db/alembic.ini upgrade head" in compose
