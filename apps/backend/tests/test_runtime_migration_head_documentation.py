"""US3 documentation checks for migration-head runtime expectations."""

from pathlib import Path


def test_agents_migration_head_documents_dynamic_runtime_expectation() -> None:
    """Ensure AGENTS guidance documents dynamic Alembic-head runtime checks."""
    agents = Path("AGENTS.md").read_text(encoding="utf-8")

    assert "current Alembic head" in agents
    assert "do not pin a fixed revision in compose" in agents


def test_quickstart_mentions_dynamic_migration_head_enforcement() -> None:
    """Ensure quickstart documents migration-head enforcement without fixed revision pins."""
    quickstart = Path("specs/019-real-backend-api/quickstart.md").read_text(encoding="utf-8")

    assert "alembic -c libs/db/alembic.ini heads" in quickstart
    assert "current Alembic head" in quickstart
