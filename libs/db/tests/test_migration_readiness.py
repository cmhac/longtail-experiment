"""Foundational migration readiness contract tests."""

from __future__ import annotations

from pathlib import Path


def test_alembic_ini_config_exists_with_script_location() -> None:
    alembic_ini = Path("libs/db/alembic.ini")
    assert alembic_ini.exists()
    content = alembic_ini.read_text(encoding="utf-8")
    assert "script_location = libs/db/alembic" in content


def test_migration_scripts_have_strict_mode_headers() -> None:
    scripts = [
        Path("tools/quality/local-stack/run-db-migrations.sh"),
        Path("tools/quality/local-stack/check-db-revision.sh"),
    ]
    for script in scripts:
        text = script.read_text(encoding="utf-8")
        assert text.startswith("#!/usr/bin/env bash\nset -euo pipefail\n")


def test_migration_command_contracts_present() -> None:
    run_script = Path("tools/quality/local-stack/run-db-migrations.sh").read_text(
        encoding="utf-8"
    )
    check_script = Path("tools/quality/local-stack/check-db-revision.sh").read_text(
        encoding="utf-8"
    )
    assert "alembic -c \"$ALEMBIC_INI\" upgrade head" in run_script
    assert "alembic -c \"$ALEMBIC_INI\" current" in check_script
