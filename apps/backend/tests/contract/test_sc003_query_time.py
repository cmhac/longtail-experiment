"""SC-003 query-time verification tests for manual workflow latency."""

from __future__ import annotations

import json
from pathlib import Path

_SCENARIO_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "sc003_query_scenarios.json"
_QUERY_TIME_TARGET_MS = 2000


def test_sc003_filter_to_results_time_within_target() -> None:
    """All manual workflow scenarios should stay within latency target."""
    payload = json.loads(_SCENARIO_PATH.read_text(encoding="utf-8"))

    assert payload["target_ms"] == _QUERY_TIME_TARGET_MS
    assert all(
        int(scenario["elapsed_ms"]) <= _QUERY_TIME_TARGET_MS for scenario in payload["scenarios"]
    )
