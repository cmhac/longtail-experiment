"""Reusable fixture helpers for trend-analysis test scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

MONTHS_PER_YEAR = 12


@dataclass(frozen=True)
class ObservationPoint:
    """Simple fixture shape for one observation sample."""

    period: date
    value: float


def make_linear_series(start: date, values: list[float]) -> list[ObservationPoint]:
    """Return a deterministic monthly-like sequence for tests."""
    points: list[ObservationPoint] = []
    year = start.year
    month = start.month
    for value in values:
        points.append(ObservationPoint(period=date(year, month, 1), value=value))
        month += 1
        if month > MONTHS_PER_YEAR:
            month = 1
            year += 1
    return points
