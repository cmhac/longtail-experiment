"""Deterministic duplicate drift classifier for ingestion records."""

from __future__ import annotations

from typing import Literal

DuplicateDriftState = Literal["accepted", "duplicate_no_op", "conflict"]


def classify_duplicate_drift(
    *,
    existing: dict[str, object] | None,
    incoming: dict[str, object],
) -> DuplicateDriftState:
    """Classify incoming record as accepted, no-op duplicate, or conflict."""
    if existing is None:
        return "accepted"

    existing_value = existing.get("value")
    incoming_value = incoming.get("value")
    existing_attributes = existing.get("attributes", {})
    incoming_attributes = incoming.get("attributes", {})
    if existing_value == incoming_value and existing_attributes == incoming_attributes:
        return "duplicate_no_op"
    return "conflict"
