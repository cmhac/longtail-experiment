"""US2 backend-facing checks for migration command surfaces."""

from pathlib import Path


def test_quickstart_references_canonical_migration_scripts() -> None:
    """Verify quickstart points to script-based migration commands."""
    quickstart = Path("specs/004-local-dev-db/quickstart.md").read_text(encoding="utf-8")
    assert "bash tools/quality/local-stack/run-db-migrations.sh" in quickstart
    assert "bash tools/quality/local-stack/check-db-revision.sh" in quickstart


def test_migration_scripts_exist_for_backend_workflow() -> None:
    """Verify migration command scripts exist for backend usage."""
    assert Path("tools/quality/local-stack/run-db-migrations.sh").exists()
    assert Path("tools/quality/local-stack/check-db-revision.sh").exists()
