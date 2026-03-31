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
        "event_timestamp": "2026-01-01T00:00:00Z",
        "dataset_id": "UNRATE",
        "direction": "up",
        "strength": "moderate",
        "start_period": "2026-01-01T00:00:00Z",
        "is_ongoing": True,
    }

    assert item["item_type"] == "trend_event"


def test_trend_span_contract_embeds_tooltip_shape() -> None:
    tooltip: TrendTooltipContract = {
        "title": "Emerging uptrend",
        "start_period": "2026-01-01T00:00:00Z",
        "direction": "up",
        "strength": "moderate",
    }
    span: TrendSpanContract = {
        "span_id": "trend-1",
        "start_x": "2026-01-01T00:00:00Z",
        "end_x": "2026-04-01T00:00:00Z",
        "direction": "up",
        "color_token": "trend-up",
        "pattern_token": "diagonal-up",
        "direction_icon": "arrow-up",
        "tooltip": tooltip,
    }

    assert span["tooltip"]["direction"] == "up"
