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
