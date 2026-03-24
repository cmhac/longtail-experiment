"""Unit tests for provider bootstrap collision checks."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
MODULE_PATH = REPO_ROOT / "tools/provider_bootstrap/collision_checks.py"
MODULE_SPEC = importlib.util.spec_from_file_location("provider_bootstrap_collision", MODULE_PATH)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
collision_checks = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(collision_checks)

ensure_output_path_available = collision_checks.ensure_output_path_available
ensure_source_key_available = collision_checks.ensure_source_key_available


def test_output_path_collision_raises(tmp_path: Path) -> None:
    """Existing output file should fail generation before write."""
    target = tmp_path / "acme_cpi_source.py"
    target.write_text("# existing\n", encoding="utf-8")

    with pytest.raises(FileExistsError):
        ensure_output_path_available(target)


def test_source_key_collision_raises(tmp_path: Path) -> None:
    """Duplicate source keys should be rejected against discovered adapters."""
    source_file = tmp_path / "acme_cpi_source.py"
    source_file.write_text(
        'SOURCE_SPEC = {"source_key": "acme_cpi"}\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        ensure_source_key_available("acme_cpi", source_dir=tmp_path)


def test_source_key_available_passes(tmp_path: Path) -> None:
    """Non-duplicated source keys should pass collision checks."""
    source_file = tmp_path / "acme_ppi_source.py"
    source_file.write_text(
        'SOURCE_SPEC = {"source_key": "acme_ppi"}\n',
        encoding="utf-8",
    )

    ensure_source_key_available("acme_cpi", source_dir=tmp_path)
