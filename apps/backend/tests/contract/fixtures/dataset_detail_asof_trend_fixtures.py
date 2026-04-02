"""Deterministic fixture builders for dataset-detail observation as-of descriptors."""

from __future__ import annotations

from typing import Any


def build_observation_asof_available_descriptor(
    *,
    observed_on: str = "2026-03-01",
    selected_lookback_points: int = 25,
) -> dict[str, Any]:
    """Return one valid available observation-level as-of descriptor."""
    return {
        "descriptor_state": "available",
        "trend_label": "mild_sustained_downtrend",
        "direction": "down",
        "strength": "mild",
        "selected_lookback_points": selected_lookback_points,
        "observed_on": observed_on,
        "reason_code": None,
    }


def build_observation_asof_unavailable_descriptor(
    *,
    reason_code: str = "missing_observation_asof_descriptor",
) -> dict[str, Any]:
    """Return one valid unavailable observation-level as-of descriptor."""
    return {
        "descriptor_state": "unavailable",
        "trend_label": None,
        "direction": None,
        "strength": None,
        "selected_lookback_points": None,
        "observed_on": None,
        "reason_code": reason_code,
    }
