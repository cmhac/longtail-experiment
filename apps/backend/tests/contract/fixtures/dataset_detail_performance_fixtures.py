"""Shared timing helpers for dataset detail performance tests."""

from __future__ import annotations

from collections.abc import Callable
from statistics import median
from time import perf_counter
from typing import Any


def measure_call_durations_ms(
    fn: Callable[[], Any],
    *,
    repetitions: int,
) -> list[float]:
    """Measure repeated call durations in milliseconds."""
    samples: list[float] = []
    for _ in range(repetitions):
        start = perf_counter()
        fn()
        elapsed_ms = (perf_counter() - start) * 1000
        samples.append(elapsed_ms)
    return samples


def median_duration_ms(samples: list[float]) -> float:
    """Return median latency for a duration sample set."""
    if not samples:
        return 0.0
    return float(median(samples))
