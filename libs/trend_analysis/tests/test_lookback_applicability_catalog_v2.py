"""US2 coverage for full lookback applicability catalog in v2."""

from __future__ import annotations

from datetime import date

from trend_analysis import LOOKBACK_CATALOG, evaluate_multi_lookbacks


def test_full_lookback_catalog_applicability_is_always_recorded() -> None:
    observations = [(date(2026, 1, day), float(100 + day)) for day in range(1, 20)]
    result = evaluate_multi_lookbacks(observations)

    assert tuple(item.lookback_points for item in result.applicability) == LOOKBACK_CATALOG
