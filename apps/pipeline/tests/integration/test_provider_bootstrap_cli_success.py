"""Integration tests for successful provider bootstrap CLI runs."""

from __future__ import annotations

import ast
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


def test_cli_generates_scaffold_successfully(tmp_path: Path) -> None:
    """CLI should create a syntactically valid scaffold for valid input."""
    result = _run_bootstrap(
        "--provider-group-key",
        "acme",
        "--source-key",
        "acme_cpi_test",
        "--module-name",
        "acme_cpi_test_source",
        "--cadence-label",
        "monthly",
        "--cron-schedule",
        "0 0 1 * *",
        "--series-item-key",
        "acme_cpi_test",
        "--canonical-series-key",
        "PRICE.US.CPI",
        "--provider-series-id",
        "CPIAUCSL",
        "--output-dir",
        str(tmp_path),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "STATUS: success" in result.stdout

    generated = tmp_path / "acme_cpi_test_source.py"
    assert generated.exists()
    ast.parse(generated.read_text(encoding="utf-8"))
