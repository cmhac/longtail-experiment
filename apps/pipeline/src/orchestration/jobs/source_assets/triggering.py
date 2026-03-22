"""Helpers for source-targeted trigger parsing and validation."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4


def normalize_requested_source_keys(
    *,
    source_key_tag: str | None,
    source_keys_tag: str | None,
) -> list[str] | None:
    """Normalize source selection tags into sorted unique source keys."""
    raw: list[str] = []
    if source_key_tag is not None and source_key_tag.strip():
        raw.append(source_key_tag)
    if source_keys_tag is not None and source_keys_tag.strip():
        raw.extend(source_keys_tag.split(","))

    normalized = sorted({item.strip() for item in raw if item.strip()})
    if not normalized:
        return None
    return normalized


def validate_source_selection(
    *,
    requested_source_keys: list[str] | None,
    available_source_keys: list[str],
) -> tuple[list[str], list[str]]:
    """Return valid and invalid source selections for a trigger request."""
    if requested_source_keys is None:
        return (available_source_keys, [])

    available = set(available_source_keys)
    valid = [source_key for source_key in requested_source_keys if source_key in available]
    invalid = [source_key for source_key in requested_source_keys if source_key not in available]
    return (valid, invalid)


def build_invalid_source_request_summary(
    *,
    requested_by: str,
    trigger_type: str,
    invalid_source_keys: list[str],
    available_source_keys: list[str],
) -> dict[str, object]:
    """Build fail-fast outcome payload for invalid source trigger requests."""
    now = datetime.now(tz=UTC)
    return {
        "run_id": f"invalid-source-request-{uuid4()}",
        "trigger_type": trigger_type,
        "requested_by": requested_by,
        "started_at": now,
        "completed_at": now,
        "source_results": [
            {
                "source_key": source_key,
                "status": "failure",
                "accepted_count": 0,
                "quarantined_count": 0,
                "failed_count": 1,
                "duplicate_no_op_count": 0,
                "conflict_count": 0,
                "outcome_reason_code": "invalid_source_key",
                "message": (
                    "unknown source key requested; "
                    f"available={','.join(sorted(available_source_keys))}"
                ),
                "visible_in_dagit": True,
                "failure_summary": f"Invalid source key requested: {source_key}",
            }
            for source_key in invalid_source_keys
        ],
        "outcome_state": "failure",
        "accepted_count": 0,
        "quarantined_count": 0,
        "failed_count": len(invalid_source_keys),
        "failed_source_count": len(invalid_source_keys),
        "duplicate_no_op_count": 0,
        "conflict_count": 0,
        "due_source_count": 0,
        "executed_source_count": 0,
        "deferred_source_count": 0,
        "not_due_source_count": 0,
    }
