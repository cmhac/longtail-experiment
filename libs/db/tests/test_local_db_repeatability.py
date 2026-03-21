"""US3 repeatability checks for local DB migration scripts."""

from __future__ import annotations

from pathlib import Path


def test_migration_scripts_avoid_destructive_reset_steps() -> None:
    run_script = Path("tools/quality/local-stack/run-db-migrations.sh").read_text(
        encoding="utf-8"
    )
    check_script = Path("tools/quality/local-stack/check-db-revision.sh").read_text(
        encoding="utf-8"
    )
    assert "down -v" not in run_script
    assert "down -v" not in check_script


def test_migration_scripts_wait_for_db_health() -> None:
    run_script = Path("tools/quality/local-stack/run-db-migrations.sh").read_text(
        encoding="utf-8"
    )
    check_script = Path("tools/quality/local-stack/check-db-revision.sh").read_text(
        encoding="utf-8"
    )
    assert "for _ in $(seq 1 30); do" in run_script
    assert '"Health":"healthy"' in run_script
    assert "for _ in $(seq 1 30); do" in check_script
    assert '"Health":"healthy"' in check_script
