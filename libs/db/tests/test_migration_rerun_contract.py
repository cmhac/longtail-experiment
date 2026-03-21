"""Contract checks for repeatable migration wrapper behavior."""

from __future__ import annotations

from pathlib import Path


def test_runner_uses_non_destructive_upgrade_head() -> None:
    run_script = Path("tools/quality/local-stack/run-db-migrations.sh").read_text(
        encoding="utf-8"
    )
    assert "upgrade head" in run_script
    assert "downgrade" not in run_script


def test_revision_check_is_deterministic() -> None:
    check_script = Path("tools/quality/local-stack/check-db-revision.sh").read_text(
        encoding="utf-8"
    )
    assert "EXPECTED_DB_REVISION" in check_script
    assert "Revision mismatch" in check_script
    assert "Revision OK" in check_script
