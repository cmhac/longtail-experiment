"""Smoke test for Dagster orchestration definitions."""

from __future__ import annotations

import sys
from pathlib import Path

from dagster import Definitions

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.definitions import defs


def test_orchestration_definitions_is_dagster_definitions() -> None:
    """The orchestration entrypoint must expose a Dagster Definitions object."""
    assert isinstance(defs, Definitions)


def test_orchestration_definitions_expose_visibility_resources() -> None:
    """Definitions should include resources needed for visibility and scheduling semantics."""
    resources = defs.resources or {}
    assert "run_repository" in resources
    assert "due_source_selector" in resources
    assert "parallel_source_executor" in resources
