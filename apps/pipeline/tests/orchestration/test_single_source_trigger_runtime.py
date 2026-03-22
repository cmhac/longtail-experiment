"""Integration tests for source-targeted trigger and validation behavior."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.source_assets.triggering import (
    build_invalid_source_request_summary,
    normalize_requested_source_keys,
    validate_source_selection,
)


def test_single_source_trigger_selects_only_one_source() -> None:
    """Valid source_key should normalize and select one source only."""
    requested = normalize_requested_source_keys(
        source_key_tag="alpha",
        source_keys_tag=None,
    )

    selected, invalid = validate_source_selection(
        requested_source_keys=requested,
        available_source_keys=["alpha", "beta"],
    )

    assert selected == ["alpha"]
    assert invalid == []


def test_invalid_source_key_is_rejected_before_run_starts() -> None:
    """Unknown source key should fail fast with a structured invalid-source summary."""
    requested = normalize_requested_source_keys(
        source_key_tag="missing-source",
        source_keys_tag=None,
    )
    selected, invalid = validate_source_selection(
        requested_source_keys=requested,
        available_source_keys=["alpha", "beta"],
    )

    payload = build_invalid_source_request_summary(
        requested_by="operator",
        trigger_type="on_demand",
        invalid_source_keys=invalid,
        available_source_keys=["alpha", "beta"],
    )

    assert selected == []
    assert payload["outcome_state"] == "failure"
    assert payload["failed_source_count"] == 1
    assert payload["source_results"][0]["outcome_reason_code"] == "invalid_source_key"
