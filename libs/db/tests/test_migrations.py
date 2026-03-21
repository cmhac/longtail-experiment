"""Migration smoke tests for baseline revision metadata."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def test_baseline_revision_metadata() -> None:
    file_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0001_contract_baseline.py"
    )
    spec = spec_from_file_location("contract_baseline", file_path)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.revision == "0001_contract_baseline"
    assert module.down_revision is None
