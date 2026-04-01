"""Trend contract payload shapes for discovery query surfaces."""

from __future__ import annotations

from typing import Literal, TypedDict


class TrendFeedItemContract(TypedDict):
    """Unified recent-feed trend event payload."""

    item_type: Literal["trend_event"]
    dataset_id: str
    source: dict[str, str]
    title: str
    direction: Literal["up", "down"]
    strength: str
    start_period: str
    latest_update_at: str
    action_links: dict[str, str]


class TrendTooltipContract(TypedDict):
    """Tooltip payload rendered for one trend span."""

    headline: str
    detail: str


class TrendSpanContract(TypedDict):
    """Dataset detail trend span payload."""

    start_period: str
    end_period: str
    direction: Literal["up", "down"]
    trend_label: str
    tooltip: TrendTooltipContract
