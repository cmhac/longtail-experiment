"""US1 backend contract tests for current canonical v2 descriptor shape."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.query.trend_descriptor_v2 import CanonicalTrendDescriptorV2


def test_current_canonical_v2_accepts_flat_direction() -> None:
    payload = CanonicalTrendDescriptorV2.model_validate(
        {
            "descriptor_version": "v2",
            "descriptor_state": "available",
            "trend_label": "flat",
            "direction": "flat",
            "confidence_score": 0.41,
            "selected_lookback_points": 25,
            "observed_on": "2026-03-01",
            "dominant_measure_family": "theil_sen",
            "reason_code": None,
        }
    )
    assert payload.direction == "flat"
