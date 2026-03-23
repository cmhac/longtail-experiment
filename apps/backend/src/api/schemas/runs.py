"""Pydantic response schemas for IngestionRun API responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer, field_validator


class IngestionRunResponse(BaseModel):
    """Projects an IngestionRun ORM row into the HTTP response shape."""

    model_config = ConfigDict(from_attributes=True)

    run_id: str
    trigger_type: str
    lifecycle_state: str
    outcome_state: str
    started_at: datetime
    completed_at: datetime | None = None
    accepted_count: int
    quarantined_count: int
    failed_count: int
    duplicate_no_op_count: int
    conflict_count: int
    due_source_count: int
    executed_source_count: int
    deferred_source_count: int
    not_due_source_count: int
    failed_source_count: int
    trigger_origin: str | None = None

    @field_serializer("started_at")
    def serialize_started_at(self, v: datetime) -> str:
        """Serialize started_at to ISO-8601 UTC string."""
        return v.isoformat()

    @field_serializer("completed_at")
    def serialize_completed_at(self, v: datetime | None) -> str | None:
        """Serialize completed_at to ISO-8601 UTC string or null."""
        return v.isoformat() if v is not None else None

    @field_validator(
        "accepted_count",
        "quarantined_count",
        "failed_count",
        "duplicate_no_op_count",
        "conflict_count",
        "due_source_count",
        "executed_source_count",
        "deferred_source_count",
        "not_due_source_count",
        "failed_source_count",
    )
    @classmethod
    def count_non_negative(cls, v: int) -> int:
        """Validate all count fields are non-negative."""
        if v < 0:
            msg = "count fields must be >= 0"
            raise ValueError(msg)
        return v
