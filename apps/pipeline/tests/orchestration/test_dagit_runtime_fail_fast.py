"""Fail-fast checks for compose-managed Dagit metadata configuration."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.runtime import validate_dagster_metadata_storage_config


def test_runtime_validation_fails_fast_when_metadata_password_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Runtime validation should fail before Dagit can start with invalid metadata env."""
    monkeypatch.setenv("DAGSTER_METADATA_DB_HOST", "127.0.0.1")
    monkeypatch.setenv("DAGSTER_METADATA_DB_PORT", "55433")
    monkeypatch.setenv("DAGSTER_METADATA_DB_NAME", "dagster_local")
    monkeypatch.setenv("DAGSTER_METADATA_DB_USER", "dagster")
    monkeypatch.setenv("DAGSTER_METADATA_DB_PASSWORD", "")

    with pytest.raises(RuntimeError, match="Missing required Dagster metadata DB"):
        validate_dagster_metadata_storage_config()


def test_compose_declares_metadata_enforcement_for_dagit() -> None:
    """Compose Dagit service should enforce metadata env validation."""
    compose_yaml = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert 'DAGSTER_METADATA_ENFORCE: "1"' in compose_yaml
