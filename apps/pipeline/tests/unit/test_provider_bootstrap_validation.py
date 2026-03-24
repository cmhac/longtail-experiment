"""Unit tests for provider bootstrap validation helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
MODULE_PATH = REPO_ROOT / "tools/provider_bootstrap/validation.py"
MODULE_SPEC = importlib.util.spec_from_file_location("provider_bootstrap_validation", MODULE_PATH)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
validation = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(validation)

normalize_module_name = validation.normalize_module_name
validate_cadence_label = validation.validate_cadence_label
validate_canonical_key = validation.validate_canonical_key
validate_cron_schedule = validation.validate_cron_schedule
validate_series_alignment = validation.validate_series_alignment
validate_snake_identifier = validation.validate_snake_identifier


def test_normalize_module_name_adds_suffix() -> None:
    """Module names without suffix should be normalized to *_source."""
    assert normalize_module_name("acme_cpi") == "acme_cpi_source"


def test_normalize_module_name_preserves_suffix() -> None:
    """Module names already ending with *_source should stay unchanged."""
    assert normalize_module_name("acme_cpi_source") == "acme_cpi_source"


def test_validate_snake_identifier_rejects_uppercase() -> None:
    """Snake-case validator should reject uppercase identifiers."""
    with pytest.raises(ValueError):
        validate_snake_identifier("Acme", field="provider_group_key")


def test_validate_cadence_label_rejects_unknown() -> None:
    """Cadence validator should reject unsupported labels."""
    with pytest.raises(ValueError):
        validate_cadence_label("yearly")


def test_validate_cron_schedule_requires_five_fields() -> None:
    """Cron validator should require exactly five fields."""
    with pytest.raises(ValueError):
        validate_cron_schedule("0 0 * *")


def test_validate_canonical_key_rejects_lowercase() -> None:
    """Canonical key validator should enforce uppercase dotted format."""
    with pytest.raises(ValueError):
        validate_canonical_key("price.us.cpi")


def test_validate_series_alignment_requires_equal_lengths() -> None:
    """Series arrays should have equal lengths across aligned arguments."""
    with pytest.raises(ValueError):
        validate_series_alignment(
            series_item_keys=["acme_cpi"],
            canonical_series_keys=["PRICE.US.CPI", "PRICE.US.PPI"],
            provider_series_ids=["CPIAUCSL"],
        )
