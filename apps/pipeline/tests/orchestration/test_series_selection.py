"""Tests for series-item selection normalization and resolution."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.source_assets.series_catalog import SeriesCatalogEntry
from src.orchestration.jobs.source_assets.series_selection import (
    normalize_requested_series_item_keys,
    resolve_series_selection,
)


def test_series_selection_normalization_from_tags() -> None:
    """Normalization should deduplicate and trim series keys from both tag forms."""
    normalized = normalize_requested_series_item_keys(
        series_item_key_tag=" fred_fedfunds ",
        series_item_keys_tag="fred_gasregw,fred_fedfunds",
    )

    assert normalized == ["fred_fedfunds", "fred_gasregw"]


def test_series_selection_resolution_derives_source_from_catalog() -> None:
    """Resolution should derive owning source key from the series catalog map."""
    resolution = resolve_series_selection(
        requested_series_item_keys=["fred_gasregw"],
        catalog_entries=(
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
        ),
        selected_source_keys=None,
    )

    assert resolution.invalid_series_item_keys == []
    assert resolution.selected_source_keys == ["fred_fedfunds"]
    assert resolution.selected_series_item_keys == ["fred_gasregw"]


def test_series_selection_resolution_reports_invalid_keys() -> None:
    """Resolution should report invalid series item keys when missing from catalog."""
    resolution = resolve_series_selection(
        requested_series_item_keys=["unknown"],
        catalog_entries=(),
        selected_source_keys=None,
    )

    assert resolution.invalid_series_item_keys == ["unknown"]
    assert resolution.selected_source_keys == []
    assert resolution.selected_series_item_keys == []


def test_series_selection_resolution_respects_selected_source_constraints() -> None:
    """Resolution should filter derived source keys by explicit source selection constraints."""
    resolution = resolve_series_selection(
        requested_series_item_keys=["fred_gasregw"],
        catalog_entries=(
            SeriesCatalogEntry(
                source_key="fred_fedfunds",
                provider_group_key="fred",
                series_item_key="fred_gasregw",
                canonical_series_key="ENERGY.US.GASREGW",
                ownership_mode="grouped",
            ),
        ),
        selected_source_keys=["example_source"],
    )

    assert resolution.selected_source_keys == []
    assert resolution.selected_series_item_keys == ["fred_gasregw"]
