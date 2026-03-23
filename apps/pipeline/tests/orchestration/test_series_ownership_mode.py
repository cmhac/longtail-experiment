"""Foundational tests for ownership-mode overlap validation."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.source_assets.ownership_mode import (
    SeriesOwnershipModeRecord,
    validate_ownership_mode_windows,
)


def test_ownership_mode_validation_allows_non_overlapping_windows() -> None:
    """Validation should allow contiguous non-overlapping ownership windows."""
    records = [
        SeriesOwnershipModeRecord(
            series_item_key="fred_gasregw",
            owner_adapter_key="fred_grouped",
            mode="grouped",
            effective_from=datetime(2026, 1, 1, tzinfo=UTC),
            effective_to=datetime(2026, 2, 1, tzinfo=UTC),
        ),
        SeriesOwnershipModeRecord(
            series_item_key="fred_gasregw",
            owner_adapter_key="fred_gasregw",
            mode="split",
            effective_from=datetime(2026, 2, 1, tzinfo=UTC),
            effective_to=None,
        ),
    ]

    validate_ownership_mode_windows(records)


def test_ownership_mode_validation_rejects_overlap() -> None:
    """Validation should reject overlapping ownership windows for the same series."""
    records = [
        SeriesOwnershipModeRecord(
            series_item_key="fred_gasregw",
            owner_adapter_key="fred_grouped",
            mode="grouped",
            effective_from=datetime(2026, 1, 1, tzinfo=UTC),
            effective_to=datetime(2026, 2, 5, tzinfo=UTC),
        ),
        SeriesOwnershipModeRecord(
            series_item_key="fred_gasregw",
            owner_adapter_key="fred_gasregw",
            mode="split",
            effective_from=datetime(2026, 2, 1, tzinfo=UTC),
            effective_to=None,
        ),
    ]

    with pytest.raises(ValueError, match="overlapping ownership windows"):
        validate_ownership_mode_windows(records)
