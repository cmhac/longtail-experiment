"""Trend analysis library package."""

from .classifier import (
    LOOKBACK_CATALOG,
    analyze_series,
    compute_canonical_descriptor,
    evaluate_multi_lookbacks,
)
from .models import (
    CadenceDecisionResult,
    CanonicalTrendDescriptorResult,
    LookbackApplicabilityResult,
    LookbackTrendSnapshotResult,
    MultiLookbackEvaluationResult,
    TrendAnalysisResult,
    TrendSignature,
)
from .version import CANONICAL_WEIGHTING_VERSION, LIBRARY_VERSION

__all__ = [
    "CANONICAL_WEIGHTING_VERSION",
    "CadenceDecisionResult",
    "CanonicalTrendDescriptorResult",
    "LOOKBACK_CATALOG",
    "LookbackApplicabilityResult",
    "LookbackTrendSnapshotResult",
    "LIBRARY_VERSION",
    "MultiLookbackEvaluationResult",
    "TrendAnalysisResult",
    "TrendSignature",
    "analyze_series",
    "compute_canonical_descriptor",
    "evaluate_multi_lookbacks",
]
