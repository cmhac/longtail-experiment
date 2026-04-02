"""Compatibility tests for legacy orchestration jobs.sources package exports."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.orchestration.jobs.sources as legacy_sources
from src.sources import FRED_FEDFUNDS_SOURCE_KEY, build_fred_fedfunds_source_workflow


def test_legacy_sources_package_reexports_fred_workflow_symbols() -> None:
    """Legacy package should continue re-exporting FRED symbols for compatibility."""
    assert legacy_sources.FRED_FEDFUNDS_SOURCE_KEY == FRED_FEDFUNDS_SOURCE_KEY
    assert legacy_sources.build_fred_fedfunds_source_workflow is build_fred_fedfunds_source_workflow
    assert set(legacy_sources.__all__) == {
        "FRED_FEDFUNDS_SOURCE_KEY",
        "build_fred_fedfunds_source_workflow",
    }

