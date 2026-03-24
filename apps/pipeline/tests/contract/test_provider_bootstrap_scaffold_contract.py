"""Contract tests for generated provider scaffold shape."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = REPO_ROOT / "tools/provider_bootstrap/bootstrap_provider.py"


def test_generated_scaffold_contains_required_sections(tmp_path: Path) -> None:
    """Generated scaffold should include required workflow and manifest sections."""
    result = subprocess.run(  # noqa: S603
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--provider-group-key",
            "acme",
            "--source-key",
            "acme_contract",
            "--module-name",
            "acme_contract_source",
            "--cadence-label",
            "monthly",
            "--cron-schedule",
            "0 0 1 * *",
            "--series-item-key",
            "acme_contract",
            "--canonical-series-key",
            "PRICE.US.CPI",
            "--provider-series-id",
            "CPIAUCSL",
            "--output-dir",
            str(tmp_path),
        ],  # noqa: S607
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    generated = tmp_path / "acme_contract_source.py"
    text = generated.read_text(encoding="utf-8")

    assert "SOURCE_SPEC" in text
    assert "SourceWorkflowRegistration" in text
    assert "build_acme_contract_source_workflow" in text
    assert '"source_key": ACME_ACME_CONTRACT_SOURCE_KEY' in text
