"""Pydantic response schemas for SourceEligibilitySnapshot API responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer

VALID_ELIGIBILITY_STATES = frozenset(
    {"due", "not_due", "skipped_inactive", "skipped_invalid_policy"}
)


class SourceEligibilityResponse(BaseModel):
    """Projects a SourceEligibilitySnapshot ORM row into the HTTP response shape."""

    model_config = ConfigDict(from_attributes=True)

    run_id: str
    source_key: str
    eligibility_state: str
    reason_code: str
    evaluated_at: datetime
    due_at: datetime | None = None
    selected_for_execution: bool

    @field_serializer("evaluated_at")
    def serialize_evaluated_at(self, v: datetime) -> str:
        """Serialize evaluated_at to ISO-8601 UTC string."""
        return v.isoformat()

    @field_serializer("due_at")
    def serialize_due_at(self, v: datetime | None) -> str | None:
        """Serialize due_at to ISO-8601 UTC string or null."""
        return v.isoformat() if v is not None else None
