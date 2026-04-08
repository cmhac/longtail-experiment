"""Contract tests for trend descriptor v2 migration metadata and scope."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def test_trend_descriptor_v2_migration_metadata() -> None:
    file_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0016_trend_descriptor_v2_contract.py"
    )
    spec = spec_from_file_location("trend_descriptor_v2_contract", file_path)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.revision == "0016_trend_descriptor_v2_contract"
    assert module.down_revision == "0015_trend_notifications"


def test_trend_descriptor_v2_migration_adds_expected_contract_fields() -> None:
    migration_text = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0016_trend_descriptor_v2_contract.py"
    ).read_text(encoding="utf-8")

    required_tokens = (
        "descriptor_version",
        "confidence_score",
        "dominant_measure_family",
        "theil_sen_slope",
        "kendall_tau",
        "ols_r_squared",
        "preprocessing",
        "reason_code",
        "flat",
    )
    for token in required_tokens:
        assert token in migration_text
