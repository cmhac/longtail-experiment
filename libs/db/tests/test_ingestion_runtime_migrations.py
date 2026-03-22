"""Migration tests for ingestion runtime tables."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def test_runtime_migration_metadata() -> None:
    file_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0002_ingestion_runtime_and_conflicts.py"
    )
    spec = spec_from_file_location("ingestion_runtime", file_path)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.revision == "0002_ingestion_runtime_conflicts"
    assert module.down_revision == "0001_contract_baseline"


def test_runtime_migration_creates_expected_tables() -> None:
    migration_text = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0002_ingestion_runtime_and_conflicts.py"
    ).read_text(encoding="utf-8")

    for table_name in (
        "ingestion_runs",
        "source_run_locks",
        "source_run_outcomes",
        "conflict_records",
    ):
        assert f'"{table_name}"' in migration_text
