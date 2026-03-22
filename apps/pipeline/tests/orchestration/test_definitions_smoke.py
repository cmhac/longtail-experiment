"""Smoke test for Dagster orchestration definitions."""

from __future__ import annotations

import sys
from pathlib import Path

from dagster import Definitions

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.definitions import defs
from src.orchestration.jobs.sources.fred_fedfunds_source import FRED_FEDFUNDS_SOURCE_KEY
from src.orchestration.runtime import build_ingest_runtime


def test_orchestration_definitions_is_dagster_definitions() -> None:
    """The orchestration entrypoint must expose a Dagster Definitions object."""
    assert isinstance(defs, Definitions)


def test_orchestration_definitions_expose_visibility_resources() -> None:
    """Definitions should include resources needed for visibility and scheduling semantics."""
    resources = defs.resources or {}
    assert "run_repository" in resources
    assert "due_source_selector" in resources
    assert "parallel_source_executor" in resources


def test_runtime_builder_registers_expected_sources() -> None:
    """Runtime wiring should register dummy, example, and FRED source workflows."""
    runtime = build_ingest_runtime()
    registry = runtime.run_coordinator._workflow_registry  # noqa: SLF001 - smoke assertion

    assert registry.list_source_keys() == [
        "dummy_source",
        "example_source",
        FRED_FEDFUNDS_SOURCE_KEY,
    ]
