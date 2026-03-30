"""Contract tests for generated provider scaffold shape."""

from __future__ import annotations

import importlib.util
import sys
from collections.abc import Callable
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[4] / "tools/provider_bootstrap/bootstrap_provider.py"


def _load_main() -> Callable[[list[str]], int]:
    script_dir = str(SCRIPT_PATH.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    spec = importlib.util.spec_from_file_location("bootstrap_provider", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load bootstrap_provider module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    main_fn = getattr(module, "main", None)
    if not callable(main_fn):
        raise RuntimeError("bootstrap_provider.main is not callable")
    return main_fn


def test_generated_scaffold_contains_required_sections(tmp_path: Path, capsys) -> None:
    """Generated scaffold should include required workflow and manifest sections."""
    exit_code = _load_main()(
        [
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
            "--source-title",
            "ACME Contract Source",
            "--source-description",
            "Contract scaffold for ACME price data.",
            "--output-dir",
            str(tmp_path),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0, captured.out + captured.err
    generated = tmp_path / "acme_contract_source.py"
    text = generated.read_text(encoding="utf-8")

    assert "SOURCE_SPEC" in text
    assert "SourceWorkflowRegistration" in text
    assert "build_acme_contract_source_workflow" in text
    assert '"source_key": ACME_ACME_CONTRACT_SOURCE_KEY' in text
    assert 'SOURCE_TITLE = "ACME Contract Source"' in text
    assert 'SOURCE_DESCRIPTION = "Contract scaffold for ACME price data."' in text
    assert '"title": SOURCE_TITLE' in text
    assert '"description": SOURCE_DESCRIPTION' in text
