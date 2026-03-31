"""Trend analysis library package."""

from .classifier import analyze_series
from .models import TrendAnalysisResult, TrendSignature
from .version import LIBRARY_VERSION

__all__ = [
    "LIBRARY_VERSION",
    "TrendAnalysisResult",
    "TrendSignature",
    "analyze_series",
]
