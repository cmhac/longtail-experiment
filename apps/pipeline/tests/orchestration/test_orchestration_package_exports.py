"""Package export smoke tests for orchestration subpackages."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.orchestration.jobs.sources as source_packages
import src.orchestration.sensors as sensor_packages


def test_orchestration_subpackage_imports_are_loadable() -> None:
    """Subpackage modules should import successfully for runtime wiring."""
    assert source_packages is not None
    assert sensor_packages is not None
