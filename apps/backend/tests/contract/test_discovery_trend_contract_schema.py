"""Foundational contract smoke tests for discovery trend payload types."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.discovery_trends import (
    TrendFeedItemContract,
    TrendSpanContract,
    TrendTooltipContract,
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


def test_trend_span_contract_embeds_tooltip_shape() -> None:
    tooltip: TrendTooltipContract = {
        "headline": "Emerging uptrend",
        "detail": "Moderate increase through Q1",
    }
    span: TrendSpanContract = {
        "start_period": "2026-01-01",
        "end_period": "2026-04-01",
        "direction": "up",
        "trend_label": "moderate_uptrend",
        "tooltip": tooltip,
    }

    assert span["tooltip"]["headline"] == "Emerging uptrend"
