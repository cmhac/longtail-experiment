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

EXPECTED_LOOKBACK_POINTS = 25


def test_trend_feed_item_contract_minimal_shape() -> None:
    item: TrendFeedItemContract = {
        "item_type": "trend_event",
        "dataset_id": "UNRATE",
        "source": {"id": "bls", "name": "BLS"},
        "title": "Unemployment trend",
        "direction": "up",
        "confidence_score": 0.66,
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
        "descriptor_version": "v2",
        "descriptor_state": "available",
        "trend_label": "moderate_uptrend",
        "direction": "up",
        "confidence_score": 0.66,
        "selected_lookback_points": 25,
        "observed_on": "2026-01-01",
        "dominant_measure_family": "theil_sen",
        "reason_code": None,
    }
    assert descriptor["descriptor_state"] == "available"


def test_lookback_snapshot_contract_shape() -> None:
    snapshot: LookbackTrendSnapshotContract = {
        "lookback_points": 25,
        "applicability_state": "applicable",
        "descriptor_state": "available",
        "trend_label": "moderate_uptrend",
        "direction": "up",
        "confidence_score": 0.66,
        "dominant_measure_family": "theil_sen",
        "theil_sen_slope": 0.21,
        "theil_sen_low_slope": 0.11,
        "theil_sen_high_slope": 0.29,
        "kendall_tau": 0.34,
        "kendall_p_value": 0.02,
        "preprocessing": {
            "smoothing_method": "none",
            "smoothing_parameters": {},
            "seasonal_adjustment_method": "none",
            "seasonal_periods": [],
            "seasonal_reliability_state": "not_applicable",
            "preprocess_version": "v2",
        },
        "ols_diagnostics": {
            "slope": 0.2,
            "intercept": 3.0,
            "r_squared": 0.52,
            "p_value": 0.03,
        },
        "reason_code": None,
    }
    assert snapshot["lookback_points"] == EXPECTED_LOOKBACK_POINTS
