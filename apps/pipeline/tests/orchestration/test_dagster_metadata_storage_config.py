"""Tests for Dagster metadata PostgreSQL configuration guards."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.runtime import (
    REQUIRED_DAGSTER_METADATA_ENV_VARS,
    validate_dagster_metadata_storage_config,
)


def test_validate_metadata_storage_config_raises_when_any_value_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Validation should fail hard when required metadata DB values are missing."""
    for key in REQUIRED_DAGSTER_METADATA_ENV_VARS:
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(RuntimeError, match="Missing required Dagster metadata DB"):
        validate_dagster_metadata_storage_config()


def test_validate_metadata_storage_config_returns_expected_mapping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Validation should return resolved metadata config when all vars are present."""
    monkeypatch.setenv("DAGSTER_METADATA_DB_HOST", "dagster_db")
    monkeypatch.setenv("DAGSTER_METADATA_DB_PORT", "5432")
    monkeypatch.setenv("DAGSTER_METADATA_DB_NAME", "dagster_local")
    monkeypatch.setenv("DAGSTER_METADATA_DB_USER", "dagster")
    monkeypatch.setenv("DAGSTER_METADATA_DB_PASSWORD", "secret")

    config = validate_dagster_metadata_storage_config()

    assert config["DAGSTER_METADATA_DB_HOST"] == "dagster_db"
    assert config["DAGSTER_METADATA_DB_PORT"] == "5432"
    assert config["DAGSTER_METADATA_DB_NAME"] == "dagster_local"
    assert config["DAGSTER_METADATA_DB_USER"] == "dagster"
    assert config["DAGSTER_METADATA_DB_PASSWORD"] == "secret"


def test_dagster_yaml_declares_postgres_backed_storage() -> None:
    """Local Dagster instance config should use dagster_postgres for all storages."""
    dagster_yaml = Path("apps/pipeline/dagster.yaml").read_text(encoding="utf-8")

    assert "module: dagster_postgres.run_storage" in dagster_yaml
    assert "module: dagster_postgres.event_log" in dagster_yaml
    assert "module: dagster_postgres.schedule_storage" in dagster_yaml
    assert "sqlite" not in dagster_yaml.lower()
