"""Legacy source adapter package kept only for package import compatibility."""

from src.sources import FRED_FEDFUNDS_SOURCE_KEY, build_fred_fedfunds_source_workflow

__all__ = [
    "FRED_FEDFUNDS_SOURCE_KEY",
    "build_fred_fedfunds_source_workflow",
]
