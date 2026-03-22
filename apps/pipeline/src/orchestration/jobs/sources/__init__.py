"""Source adapter examples for orchestration onboarding."""

from .dummy_source import DUMMY_SOURCE_KEY, build_dummy_source_workflow
from .example_source import EXAMPLE_SOURCE_KEY, build_example_source_workflow
from .fred_fedfunds_source import FRED_FEDFUNDS_SOURCE_KEY, build_fred_fedfunds_source_workflow
from .implementation_window_source import (
    IMPLEMENTATION_WINDOW_SOURCE_KEY,
    build_implementation_window_source_workflow,
)

__all__ = [
    "DUMMY_SOURCE_KEY",
    "EXAMPLE_SOURCE_KEY",
    "FRED_FEDFUNDS_SOURCE_KEY",
    "IMPLEMENTATION_WINDOW_SOURCE_KEY",
    "build_dummy_source_workflow",
    "build_example_source_workflow",
    "build_fred_fedfunds_source_workflow",
    "build_implementation_window_source_workflow",
]
