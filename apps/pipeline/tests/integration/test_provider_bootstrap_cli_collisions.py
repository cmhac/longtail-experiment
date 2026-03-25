"""Integration tests for provider bootstrap collision handling."""

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


def _run_bootstrap(*args: str, capsys) -> tuple[int, str, str]:
    exit_code = _load_main()(list(args))
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


def test_cli_rejects_existing_output_path(tmp_path: Path, capsys) -> None:
    """CLI should fail with file_exists when output adapter already exists."""
    existing = tmp_path / "acme_cpi_collision_source.py"
    existing.write_text("# existing file\n", encoding="utf-8")

    exit_code, stdout, _ = _run_bootstrap(
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
        capsys=capsys,
    )

    assert exit_code == 1
    assert "ERROR_CODE: file_exists" in stdout
