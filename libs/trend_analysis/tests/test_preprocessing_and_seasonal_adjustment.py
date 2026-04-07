"""US1 preprocessing and seasonal routing tests."""

from __future__ import annotations

from trend_analysis.preprocessing import apply_ewma
from trend_analysis.seasonal_adjustment import seasonal_method_for_cadence


def test_ewma_preprocessing_returns_metadata() -> None:
    values, metadata = apply_ewma([1.0, 2.0, 3.0, 4.0])

    assert len(values) == 4
    assert metadata.smoothing_method == "ewma"
    assert metadata.preprocess_version


def test_seasonal_routing_uses_stl_for_weekly_monthly_and_none_for_daily() -> None:
    assert seasonal_method_for_cadence("weekly") == "stl"
    assert seasonal_method_for_cadence("monthly") == "stl"
    assert seasonal_method_for_cadence("daily") == "none"
