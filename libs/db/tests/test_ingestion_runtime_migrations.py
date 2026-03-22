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


def test_schedule_eligibility_migration_metadata() -> None:
    file_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0003_source_schedule_and_eligibility.py"
    )
    spec = spec_from_file_location("source_schedule_and_eligibility", file_path)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.revision == "0003_sched_eligibility"
    assert module.down_revision == "0002_ingestion_runtime_conflicts"


def test_schedule_eligibility_migration_creates_expected_tables() -> None:
    migration_text = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0003_source_schedule_and_eligibility.py"
    ).read_text(encoding="utf-8")

    for table_name in (
        "source_schedule_policies",
        "source_eligibility_snapshots",
    ):
        assert f'"{table_name}"' in migration_text


def test_observation_store_migration_metadata() -> None:
    file_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0004_observation_store.py"
    )
    spec = spec_from_file_location("observation_store", file_path)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.revision == "0004_observation_store"
    assert module.down_revision == "0003_sched_eligibility"


def test_observation_store_migration_creates_expected_tables() -> None:
    migration_text = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0004_observation_store.py"
    ).read_text(encoding="utf-8")

    for table_name in (
        "data_series",
        "observations",
    ):
        assert f'"{table_name}"' in migration_text

    for required_fragment in (
        '"source_profiles"',
        '"frequency_granularity"',
        '"created_at"',
        '"source_profile_id"',
        '"series_id"',
        '"attributes"',
        '"uq_observation_series_date"',
    ):
        assert required_fragment in migration_text
