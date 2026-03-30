"""Integration tests for invalid provider bootstrap CLI inputs."""

from __future__ import annotations

import importlib.util
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[4] / "tools/provider_bootstrap/bootstrap_provider.py"
ARGPARSE_EXIT_CODE = 2


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


def _run_bootstrap(*args: str, capsys) -> tuple[int, str, str]:
    exit_code = _load_main()(list(args))
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


def test_cli_rejects_invalid_cadence(tmp_path: Path, capsys) -> None:
    """CLI should return invalid_input for unsupported cadence labels."""
    exit_code, stdout, _ = _run_bootstrap(
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
        "--source-title",
        "ACME Bad",
        "--source-description",
        "Invalid cadence example.",
        "--output-dir",
        str(tmp_path),
        capsys=capsys,
    )

    assert exit_code == 1
    assert "STATUS: failure" in stdout
    assert "ERROR_CODE: invalid_input" in stdout


def test_cli_rejects_missing_source_title(tmp_path: Path, capsys) -> None:
    """CLI should fail fast when source title is omitted."""
    with pytest.raises(SystemExit) as exc_info:
        _load_main()(
            [
                "--provider-group-key",
                "acme",
                "--source-key",
                "acme_missing_title",
                "--module-name",
                "acme_missing_title_source",
                "--cadence-label",
                "monthly",
                "--cron-schedule",
                "0 0 1 * *",
                "--series-item-key",
                "acme_missing_title",
                "--canonical-series-key",
                "PRICE.US.CPI",
                "--provider-series-id",
                "CPIAUCSL",
                "--source-description",
                "Missing title example.",
                "--output-dir",
                str(tmp_path),
            ]
        )

    captured = capsys.readouterr()
    assert exc_info.value.code == ARGPARSE_EXIT_CODE
    assert "--source-title" in captured.err
