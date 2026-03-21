"""Pipeline smoke tests for placeholder module behavior."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import health_message


def test_pipeline_placeholder_smoke() -> None:
    """Ensure pipeline placeholder message returns the expected static value."""
    assert health_message() == "pipeline-ok"
