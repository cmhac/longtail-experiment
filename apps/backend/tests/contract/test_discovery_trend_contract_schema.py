"""Foundational contract smoke tests for discovery trend payload types."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.discovery_trends import (
    CanonicalTrendDescriptorContract,
    LookbackTrendSnapshotContract,
    TrendFeedItemContract,
)


def test_trend_feed_item_contract_minimal_shape() -> None:
    item: TrendFeedItemContract = {
        "item_type": "trend_event",
        "dataset_id": "UNRATE",
        "source": {"id": "bls", "name": "BLS"},
        "title": "Unemployment trend",
        "direction": "up",
        "strength": "moderate",
        "start_period": "2026-01-01",
        "latest_update_at": "2026-01-01",
        "action_links": {
            "view_table_href": "/datasets/UNRATE",
            "download_csv_href": "/api/datasets/UNRATE.csv",
        },
    }

    assert item["item_type"] == "trend_event"


def test_canonical_descriptor_contract_shape() -> None:
    descriptor: CanonicalTrendDescriptorContract = {
        "descriptor_state": "available",
        "trend_label": "moderate_uptrend",
        "direction": "up",
        "strength": "moderate",
        "selected_lookback_points": 25,
        "observed_on": "2026-01-01",
        "reason_code": None,
    }
    assert descriptor["descriptor_state"] == "available"


def test_lookback_snapshot_contract_shape() -> None:
    snapshot: LookbackTrendSnapshotContract = {
        "lookback_points": 25,
        "applicability_state": "applicable",
        "outcome_state": "significant_trend",
        "trend_label": "moderate_uptrend",
        "direction": "up",
        "strength": "moderate",
        "reason_code": None,
    }
    assert snapshot["lookback_points"] == 25
