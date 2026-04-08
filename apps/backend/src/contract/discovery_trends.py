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
    confidence_score: float | None
    start_period: str
    latest_update_at: str
    action_links: dict[str, str]


class CanonicalTrendDescriptorContract(TypedDict):
    """Dataset detail canonical trend descriptor payload."""

    descriptor_version: Literal["v2"]
    descriptor_state: Literal["available", "unavailable"]
    trend_label: str | None
    direction: Literal["up", "down", "flat"] | None
    confidence_score: float | None
    dominant_measure_family: Literal["theil_sen", "mixed", "none"]
    selected_lookback_points: int | None
    observed_on: str | None
    reason_code: str | None


class LookbackTrendSnapshotContract(TypedDict):
    """Dataset detail per-lookback trend snapshot payload."""

    lookback_points: int
    applicability_state: Literal["applicable", "inapplicable"]
    descriptor_state: Literal["available", "unavailable"]
    trend_label: str | None
    direction: Literal["up", "down", "flat"] | None
    confidence_score: float | None
    dominant_measure_family: Literal["theil_sen", "mixed", "none"] | None
    theil_sen_slope: float | None
    theil_sen_low_slope: float | None
    theil_sen_high_slope: float | None
    kendall_tau: float | None
    kendall_p_value: float | None
    preprocessing: dict[str, object]
    ols_diagnostics: dict[str, float | None]
    reason_code: str | None
