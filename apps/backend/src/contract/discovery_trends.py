"""Trend contract payload shapes for discovery surfaces."""

from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


class TrendFeedItemContract(TypedDict):
    """Unified recent-feed trend event payload."""

    item_type: Literal["trend_event"]
    event_timestamp: str
    dataset_id: str
    direction: Literal["up", "down", "flat"]
    strength: str
    start_period: str
    end_period: NotRequired[str | None]
    is_ongoing: bool


class TrendTooltipContract(TypedDict):
    """Tooltip payload rendered for one trend span."""

    title: str
    start_period: str
    direction: Literal["up", "down", "flat"]
    strength: str
    end_period: NotRequired[str | None]
    seasonality_classification: NotRequired[str]


class TrendSpanContract(TypedDict):
    """Dataset detail trend span payload."""

    span_id: str
    start_x: str
    end_x: str
    direction: Literal["up", "down", "flat"]
    color_token: str
    pattern_token: str
    direction_icon: str
    tooltip: TrendTooltipContract
