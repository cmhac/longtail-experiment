"""Integration tests for provider bootstrap collision handling."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = REPO_ROOT / "tools/provider_bootstrap/bootstrap_provider.py"


def _run_bootstrap(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT_PATH), *args],  # noqa: S607
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_rejects_existing_output_path(tmp_path: Path) -> None:
    """CLI should fail with file_exists when output adapter already exists."""
    existing = tmp_path / "acme_cpi_collision_source.py"
    existing.write_text("# existing file\n", encoding="utf-8")

    result = _run_bootstrap(
        "--provider-group-key",
        "acme",
        "--source-key",
        "acme_cpi_collision",
        "--module-name",
        "acme_cpi_collision_source",
        "--cadence-label",
        "monthly",
        "--cron-schedule",
        "0 0 1 * *",
        "--series-item-key",
        "acme_cpi_collision",
        "--canonical-series-key",
        "PRICE.US.CPI",
        "--provider-series-id",
        "CPIAUCSL",
        "--output-dir",
        str(tmp_path),
    )

    assert result.returncode == 1
    assert "ERROR_CODE: file_exists" in result.stdout
