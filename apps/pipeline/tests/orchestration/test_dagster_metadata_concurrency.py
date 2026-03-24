"""Configuration-level checks supporting concurrent metadata persistence reliability."""

from __future__ import annotations

from pathlib import Path


def test_compose_includes_dedicated_dagster_metadata_database_service() -> None:
    """Compose stack should define a dedicated metadata DB service for Dagster."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "dagster_db:" in compose
    assert "DAGSTER_METADATA_DB_PASSWORD" in compose
    assert "dagster_metadata_db_data" in compose


def test_dagit_service_depends_on_metadata_database_health() -> None:
    """Dagit service should not start before metadata DB is healthy."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "depends_on:" in compose
    assert "dagster_db:" in compose
    assert "condition: service_healthy" in compose
    assert 'DAGSTER_METADATA_ENFORCE: "1"' in compose


def test_dagster_yaml_rejects_sqlite_storage_defaults() -> None:
    """Dagster storage config should be explicitly PostgreSQL-backed."""
    dagster_yaml = Path("apps/pipeline/dagster.yaml").read_text(encoding="utf-8")

    assert "PostgresRunStorage" in dagster_yaml
    assert "PostgresEventLogStorage" in dagster_yaml
    assert "PostgresScheduleStorage" in dagster_yaml
    assert "sqlite" not in dagster_yaml.lower()
