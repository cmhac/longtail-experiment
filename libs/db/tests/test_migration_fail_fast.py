"""US2 contract tests for fail-fast migration behavior."""

from __future__ import annotations

from pathlib import Path


def test_run_migrations_script_has_fail_fast_guard() -> None:
    script = Path("tools/quality/local-stack/run-db-migrations.sh").read_text(
        encoding="utf-8"
    )
    assert "set -euo pipefail" in script
    assert "if ! PYTHONPATH" in script
    assert "Migration failed before reaching head revision." in script


def test_run_migrations_script_includes_actionable_recovery_steps() -> None:
    script = Path("tools/quality/local-stack/run-db-migrations.sh").read_text(
        encoding="utf-8"
    )
    assert "docker compose ps db" in script
    assert "bash tools/quality/local-stack/run-db-migrations.sh" in script
    assert "bash tools/quality/local-stack/check-db-revision.sh" in script
