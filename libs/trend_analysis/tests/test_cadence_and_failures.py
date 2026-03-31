"""US1 tests for cadence inference and explicit cadence failures."""

from __future__ import annotations

from datetime import date

import pytest

from trend_analysis.cadence import CadenceInferenceError, infer_cadence

from .fixtures.trend_series_fixtures import make_linear_series


def test_infer_cadence_monthly_from_regular_spacing() -> None:
    """Regular month-spaced samples should infer monthly cadence."""
    points = make_linear_series(
        start=date(2023, 1, 1),
        values=[1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6],
    )

    cadence = infer_cadence([(point.period, point.value) for point in points])

    assert cadence == "monthly"


def test_infer_cadence_fails_for_irregular_spacing() -> None:
    """Mixed spacing that cannot map to one cadence should fail explicitly."""
    observations = [
        (date(2024, 1, 1), 10.0),
        (date(2024, 1, 8), 10.1),
        (date(2024, 2, 1), 10.2),
        (date(2024, 2, 9), 10.3),
        (date(2024, 3, 1), 10.4),
    ]

    with pytest.raises(CadenceInferenceError, match="cannot be inferred"):
        infer_cadence(observations)
