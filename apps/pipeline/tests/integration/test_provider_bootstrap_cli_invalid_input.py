"""Integration tests for invalid provider bootstrap CLI inputs."""

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


def test_cli_rejects_invalid_cadence(tmp_path: Path) -> None:
    """CLI should return invalid_input for unsupported cadence labels."""
    result = _run_bootstrap(
        "--provider-group-key",
        "acme",
        "--source-key",
        "acme_bad",
        "--module-name",
        "acme_bad_source",
        "--cadence-label",
        "yearly",
        "--cron-schedule",
        "0 0 1 * *",
        "--series-item-key",
        "acme_bad",
        "--canonical-series-key",
        "PRICE.US.CPI",
        "--provider-series-id",
        "CPIAUCSL",
        "--output-dir",
        str(tmp_path),
    )

    assert result.returncode == 1
    assert "STATUS: failure" in result.stdout
    assert "ERROR_CODE: invalid_input" in result.stdout
