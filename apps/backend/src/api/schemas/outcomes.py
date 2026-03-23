"""Pydantic response schemas for SourceRunOutcome API responses."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator

VALID_OUTCOME_STATES = frozenset(
    {"success", "partial_success", "failure", "not_due", "deferred", "conflict"}
)


class SourceRunOutcomeResponse(BaseModel):
    """Projects a SourceRunOutcome ORM row into the HTTP response shape."""

    model_config = ConfigDict(from_attributes=True)

    run_id: str
    source_key: str
    state: str
    accepted_count: int
    quarantined_count: int
    failed_count: int
    duplicate_no_op_count: int
    conflict_count: int
    outcome_reason_code: str | None = None
    message: str | None = None

    @field_validator("state")
    @classmethod
    def state_valid(cls, v: str) -> str:
        """Validate state is from the stable value set."""
        if v not in VALID_OUTCOME_STATES:
            msg = f"state must be one of {sorted(VALID_OUTCOME_STATES)}"
            raise ValueError(msg)
        return v

    @field_validator(
        "accepted_count",
        "quarantined_count",
        "failed_count",
        "duplicate_no_op_count",
        "conflict_count",
    )
    @classmethod
    def count_non_negative(cls, v: int) -> int:
        """Validate all count fields are non-negative."""
        if v < 0:
            msg = "count fields must be >= 0"
            raise ValueError(msg)
        return v
