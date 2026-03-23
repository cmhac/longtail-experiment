"""Pydantic response schemas for ConflictRecord API responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer, field_validator

VALID_CONFLICT_STATES = frozenset({"open", "resolved", "suppressed"})


class ConflictRecordResponse(BaseModel):
    """Projects a ConflictRecord ORM row into the HTTP response shape."""

    model_config = ConfigDict(from_attributes=True)

    conflict_id: str
    run_id: str
    source_key: str
    series_key: str
    reference_period_key: str
    existing_observation_ref: str
    incoming_record_ref: str
    conflict_type: str
    conflict_state: str
    created_at: datetime
    resolved_at: datetime | None = None

    @field_validator("conflict_state")
    @classmethod
    def conflict_state_valid(cls, v: str) -> str:
        """Validate conflict_state is from the stable value set."""
        if v not in VALID_CONFLICT_STATES:
            msg = f"conflict_state must be one of {sorted(VALID_CONFLICT_STATES)}"
            raise ValueError(msg)
        return v

    @field_serializer("created_at")
    def serialize_created_at(self, v: datetime) -> str:
        """Serialize created_at to ISO-8601 UTC string."""
        return v.isoformat()

    @field_serializer("resolved_at")
    def serialize_resolved_at(self, v: datetime | None) -> str | None:
        """Serialize resolved_at to ISO-8601 UTC string or null."""
        return v.isoformat() if v is not None else None
