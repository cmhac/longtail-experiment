"""Foundational tests for series catalog validation."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.source_assets.series_catalog import (
    SeriesCatalogEntry,
    validate_series_catalog_entries,
)


def test_series_catalog_validation_accepts_unique_entries() -> None:
    """Validation should accept entries with unique series and canonical keys."""
    entries = [
        SeriesCatalogEntry(
            source_key="fred_fedfunds",
            provider_group_key="fred",
            series_item_key="fred_fedfunds",
            canonical_series_key="INT.US.FEDFUNDS",
            ownership_mode="grouped",
        ),
        SeriesCatalogEntry(
            source_key="fred_fedfunds",
            provider_group_key="fred",
            series_item_key="fred_gasregw",
            canonical_series_key="ENERGY.US.GASREGW",
            ownership_mode="grouped",
        ),
    ]

    validate_series_catalog_entries(entries)


def test_series_catalog_validation_rejects_duplicate_series_item_key() -> None:
    """Validation should reject duplicate series item keys across entries."""
    entries = [
        SeriesCatalogEntry(
            source_key="fred_fedfunds",
            provider_group_key="fred",
            series_item_key="fred_fedfunds",
            canonical_series_key="INT.US.FEDFUNDS",
            ownership_mode="grouped",
        ),
        SeriesCatalogEntry(
            source_key="fred_gasregw",
            provider_group_key="fred",
            series_item_key="fred_fedfunds",
            canonical_series_key="ENERGY.US.GASREGW",
            ownership_mode="split",
        ),
    ]

    with pytest.raises(ValueError, match="duplicate series_item_key"):
        validate_series_catalog_entries(entries)
