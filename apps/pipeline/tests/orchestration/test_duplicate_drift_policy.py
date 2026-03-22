"""US3 duplicate drift classification tests."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.duplicate_drift_classifier import classify_duplicate_drift


def test_exact_duplicate_is_no_op() -> None:
    """Matching value and attributes should be classified as duplicate no-op."""
    state = classify_duplicate_drift(
        existing={"value": "302.5", "attributes": {"unit": "index"}},
        incoming={"value": "302.5", "attributes": {"unit": "index"}},
    )

    assert state == "duplicate_no_op"


def test_non_matching_duplicate_is_conflict() -> None:
    """Different values for the same key should become conflicts."""
    state = classify_duplicate_drift(
        existing={"value": "302.5", "attributes": {"unit": "index"}},
        incoming={"value": "303.2", "attributes": {"unit": "index"}},
    )

    assert state == "conflict"


def test_missing_existing_record_is_accepted() -> None:
    """Records without an existing baseline should be accepted."""
    state = classify_duplicate_drift(existing=None, incoming={"value": "10"})

    assert state == "accepted"
