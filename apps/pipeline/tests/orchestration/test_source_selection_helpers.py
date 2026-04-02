"""Unit tests for source and series selection helper modules."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.source_assets.series_catalog import SeriesCatalogEntry
from src.orchestration.jobs.source_assets.series_selection import (
    normalize_requested_series_item_keys,
    resolve_series_selection,
)
from src.orchestration.jobs.source_assets.triggering import (
    normalize_requested_source_keys,
    validate_source_selection,
)


def test_normalize_requested_source_keys_merges_and_sorts_unique_values() -> None:
    """Source tag normalization should merge, trim, dedupe, and sort."""
    normalized = normalize_requested_source_keys(
        source_key_tag=" fred ",
        source_keys_tag="fred,bls, ,bls",
    )
    assert normalized == ["bls", "fred"]


def test_validate_source_selection_reports_valid_and_invalid_requested_keys() -> None:
    """Source selection validation should split requested keys by availability."""
    valid, invalid = validate_source_selection(
        requested_source_keys=["fred", "unknown", "bls"],
        available_source_keys=["bls", "fred"],
    )
    assert valid == ["fred", "bls"]
    assert invalid == ["unknown"]


def test_normalize_requested_series_item_keys_merges_and_sorts_unique_values() -> None:
    """Series-item normalization should merge, trim, dedupe, and sort."""
    normalized = normalize_requested_series_item_keys(
        series_item_key_tag=" fred_fedfunds ",
        series_item_keys_tag="fred_fedfunds,fred_gasregw,fred_fedfunds",
    )
    assert normalized == ["fred_fedfunds", "fred_gasregw"]


def test_resolve_series_selection_filters_invalid_items_and_derives_sources() -> None:
    """Series selection resolution should keep valid keys and derive source scope."""
    entries = (
        SeriesCatalogEntry(
            source_key="fred",
            provider_group_key="fred",
            series_item_key="fred_fedfunds",
            canonical_series_key="INT.US.FEDFUNDS",
        ),
        SeriesCatalogEntry(
            source_key="fred",
            provider_group_key="fred",
            series_item_key="fred_gasregw",
            canonical_series_key="GAS.REG.W",
        ),
        SeriesCatalogEntry(
            source_key="bls",
            provider_group_key="bls",
            series_item_key="bls_cpi",
            canonical_series_key="PRICE.US.CPI",
        ),
    )
    result = resolve_series_selection(
        requested_series_item_keys=["fred_fedfunds", "missing_key"],
        catalog_entries=entries,
        selected_source_keys=None,
    )
    assert result.selected_source_keys == ["fred"]
    assert result.selected_series_item_keys == ["fred_fedfunds"]
    assert result.invalid_series_item_keys == ["missing_key"]
