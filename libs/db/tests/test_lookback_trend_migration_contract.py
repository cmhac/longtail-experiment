"""Contract tests for lookback trend migration and ORM schema surface."""

from __future__ import annotations

import importlib
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import CheckConstraint, Table, UniqueConstraint

models = importlib.import_module("db.models")
TrendCanonicalDescriptor = models.TrendCanonicalDescriptor
TrendLookbackEvaluation = models.TrendLookbackEvaluation
TrendLookbackSnapshot = models.TrendLookbackSnapshot


def test_lookback_migration_metadata() -> None:
    """Migration 0012 should chain from trend lifecycle tables."""
    file_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0012_lookback_trend_snapshots.py"
    )
    spec = spec_from_file_location("lookback_trend_snapshots", file_path)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.revision == "0012_lookback_trend_snapshots"
    assert module.down_revision == "0011_trend_lifecycle_tables"


def test_lookback_models_expose_expected_tables_and_key_columns() -> None:
    """Lookback ORM models should expose stable table names and key columns."""
    expected_contract = (
        (
            TrendLookbackEvaluation,
            "trend_lookback_evaluations",
            {
                "data_series_id",
                "observation_id",
                "lookback_points",
                "applicability_state",
                "reason_code",
                "created_at",
            },
        ),
        (
            TrendLookbackSnapshot,
            "trend_lookback_snapshots",
            {
                "data_series_id",
                "observation_id",
                "observed_on",
                "lookback_points",
                "outcome_state",
                "analysis_version",
                "created_at",
            },
        ),
        (
            TrendCanonicalDescriptor,
            "trend_canonical_descriptors",
            {
                "data_series_id",
                "observation_id",
                "observed_on",
                "descriptor_state",
                "weighting_version",
                "created_at",
            },
        ),
    )

    for model, expected_table_name, required_columns in expected_contract:
        table = model.__table__
        assert model.__tablename__ == expected_table_name
        for column_name in required_columns:
            assert column_name in table.columns
            assert table.columns[column_name].nullable is False


def test_lookback_constraints_and_indexes_match_expected_contract_names() -> None:
    """Constraint/index names should match stable migration and ORM contract names."""
    migration_text = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0012_lookback_trend_snapshots.py"
    ).read_text(encoding="utf-8")

    expected_names_by_table = (
        (
            TrendLookbackEvaluation.__table__,
            {
                "uq_trend_lookback_evaluations_series_observation_lookback",
            },
            {
                "ck_trend_lookback_evaluations_lookback_points_positive",
                "ck_trend_lookback_evaluations_applicability_state",
            },
            {
                "ix_trend_lookback_evaluations_series_observation",
            },
        ),
        (
            TrendLookbackSnapshot.__table__,
            {
                "uq_trend_lookback_snapshots_series_observation_lookback",
            },
            {
                "ck_trend_lookback_snapshots_lookback_points_positive",
                "ck_trend_lookback_snapshots_outcome_state",
                "ck_trend_lookback_snapshots_direction",
            },
            {
                "ix_trend_lookback_snapshots_series_observed_on",
            },
        ),
        (
            TrendCanonicalDescriptor.__table__,
            {
                "uq_trend_canonical_descriptors_series_observation",
            },
            {
                "ck_trend_canonical_descriptors_state",
                "ck_trend_canonical_descriptors_direction",
                "ck_trend_canonical_descriptors_selected_lookback_positive",
            },
            {
                "ix_trend_canonical_descriptors_series_observed_on",
            },
        ),
    )

    for (
        table,
        expected_unique,
        expected_check,
        expected_indexes,
    ) in expected_names_by_table:
        typed_table = cast(Table, table)
        unique_names = {
            constraint.name
            for constraint in typed_table.constraints
            if isinstance(constraint, UniqueConstraint) and constraint.name
        }
        check_names = {
            constraint.name
            for constraint in typed_table.constraints
            if isinstance(constraint, CheckConstraint) and constraint.name
        }
        index_names = {index.name for index in typed_table.indexes if index.name}

        assert unique_names == expected_unique
        assert check_names == expected_check
        assert index_names == expected_indexes

        for expected_name in expected_unique | expected_check | expected_indexes:
            assert expected_name in migration_text
