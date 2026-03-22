"""Regression tests for Dagster-only scheduling authority runtime state."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.source_assets.authority_state import (
    assert_dagster_only_authority,
    dagster_only_authority_state,
)


def test_runtime_disables_non_dagster_scheduler_paths() -> None:
    """Default runtime should enforce Dagster-only schedule authority."""
    authority_state = dagster_only_authority_state()

    assert authority_state.authority_mode == "dagster_only"
    assert authority_state.legacy_paths_disabled is True
    assert_dagster_only_authority(authority_state)
