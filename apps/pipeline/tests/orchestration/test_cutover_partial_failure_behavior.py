"""Regression tests for cutover partial-failure behavior."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.source_assets.authority_state import dagster_only_authority_state
from src.orchestration.jobs.source_assets.recovery import build_post_cutover_recovery_plan


def test_partial_failures_keep_dagster_as_only_scheduler() -> None:
    """Recovery plan should never re-enable legacy scheduling in partial failures."""
    authority_state = dagster_only_authority_state(partial_failure_mode=True)
    plan = build_post_cutover_recovery_plan(
        authority_state=authority_state,
        source_results=[
            {
                "source_key": "alpha",
                "status": "success",
            },
            {
                "source_key": "beta",
                "status": "failure",
            },
        ],
    )

    assert plan["authority_mode"] == "dagster_only"
    assert plan["legacy_paths_disabled"] is True
    assert plan["failed_sources"] == ["beta"]
    assert plan["requires_manual_recovery"] is True
