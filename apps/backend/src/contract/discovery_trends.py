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


class CanonicalTrendDescriptorContract(TypedDict):
    """Dataset detail canonical trend descriptor payload."""

    descriptor_state: Literal["available", "unavailable"]
    trend_label: str | None
    direction: Literal["up", "down"] | None
    strength: str | None
    selected_lookback_points: int | None
    observed_on: str | None
    reason_code: str | None


class LookbackTrendSnapshotContract(TypedDict):
    """Dataset detail per-lookback trend snapshot payload."""

    lookback_points: int
    applicability_state: Literal["applicable", "inapplicable"]
    outcome_state: Literal["significant_trend", "no_significant_trend"] | None
    trend_label: str | None
    direction: Literal["up", "down"] | None
    strength: str | None
    reason_code: str | None
