"""Trend-processing specific runtime errors."""

from __future__ import annotations


class TrendProcessingError(RuntimeError):
    """Dataset-scoped trend processing failure surfaced to orchestration."""


class TrendLookbackProcessingError(TrendProcessingError):
    """Raised when lookback snapshot processing has per-lookback failures."""
