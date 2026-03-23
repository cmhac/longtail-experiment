"""Source adapter examples for orchestration onboarding."""

from .fred_fedfunds_source import FRED_FEDFUNDS_SOURCE_KEY, build_fred_fedfunds_source_workflow

__all__ = [
    "FRED_FEDFUNDS_SOURCE_KEY",
    "build_fred_fedfunds_source_workflow",
]
