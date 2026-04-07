"""Spec 050 trend-analysis fixture series for v2 behavior coverage."""

from __future__ import annotations

from datetime import date, timedelta


def _build_points(values: list[float], *, start: date, step_days: int) -> list[tuple[date, float]]:
    return [
        (start + timedelta(days=index * step_days), value) for index, value in enumerate(values)
    ]


def noisy_near_flat_monthly() -> list[tuple[date, float]]:
    return _build_points(
        [
            100.0,
            100.4,
            99.8,
            100.2,
            100.1,
            99.9,
            100.3,
            100.0,
            99.7,
            100.2,
            100.1,
            99.9,
        ],
        start=date(2024, 1, 1),
        step_days=30,
    )


def smooth_up_monthly() -> list[tuple[date, float]]:
    return _build_points(
        [
            90.0,
            91.2,
            92.4,
            93.7,
            95.0,
            96.2,
            97.5,
            98.8,
            100.0,
            101.3,
            102.6,
            103.8,
        ],
        start=date(2024, 1, 1),
        step_days=30,
    )


def irregular_gap_series() -> list[tuple[date, float]]:
    return [
        (date(2024, 1, 1), 10.0),
        (date(2024, 1, 8), 10.4),
        (date(2024, 2, 20), 10.3),
        (date(2024, 2, 27), 10.5),
        (date(2024, 4, 15), 10.1),
        (date(2024, 4, 22), 10.0),
    ]


def regular_subdaily_series() -> list[tuple[date, float]]:
    start = date(2024, 1, 1)
    values = [
        10.0,
        10.1,
        9.9,
        10.2,
        10.3,
        10.1,
        10.4,
        10.5,
        10.2,
        10.6,
        10.7,
        10.4,
    ]
    return _build_points(values, start=start, step_days=1)
