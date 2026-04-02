"""Coverage tests for retired shared ingest schedule module."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.schedules import ingest_schedule


def test_shared_ingest_schedule_is_marked_retired() -> None:
    """Shared schedule module should expose an explicit retirement marker."""
    assert ingest_schedule.SHARED_SCHEDULE_RETIRED is True

