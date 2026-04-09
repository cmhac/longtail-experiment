"""Cadence-aware seasonal adjustment routing for v2 preprocessing."""

from __future__ import annotations

from typing import Literal


def seasonal_method_for_cadence(cadence: str) -> Literal["stl", "mstl", "none"]:
    """Return seasonal method route per current phase policy."""
    if cadence in {"weekly", "monthly"}:
        return "stl"
    return "none"
