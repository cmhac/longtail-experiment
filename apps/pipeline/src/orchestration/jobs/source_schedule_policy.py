"""
Source cadence policy schema and due-state helpers.

NOTE (Feature 011): This module is deprecated for active scheduling decisions.
Per-source Dagster schedule definitions now own cadence authority. Retained for
historical policy interpretation and backward-compatible policy hydration only.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

CadenceType = Literal["hourly", "daily", "weekly", "monthly", "custom_interval"]


class SourceSchedulePolicy(BaseModel):
    """Policy metadata describing one source cadence schedule."""

    model_config = ConfigDict(extra="forbid")

    source_key: str = Field(min_length=1)
    cadence_type: CadenceType
    cadence_value: int | None = Field(default=None, ge=1)
    timezone: str = Field(default="UTC", min_length=1)
    is_active: bool = True
    last_successful_at: datetime | None = None
    next_eligible_at: datetime | None = None
    priority_class: str = Field(default="normal", min_length=1)

    @model_validator(mode="after")
    def _validate_custom_interval(self) -> SourceSchedulePolicy:
        if self.cadence_type == "custom_interval" and self.cadence_value is None:
            raise ValueError("cadence_value is required for custom_interval cadence")
        if self.cadence_type != "custom_interval" and self.cadence_value is not None:
            raise ValueError("cadence_value is only allowed for custom_interval cadence")
        if (
            self.last_successful_at is not None
            and self.next_eligible_at is not None
            and self.next_eligible_at < self.last_successful_at
        ):
            raise ValueError("next_eligible_at must not precede last_successful_at")
        return self

    def normalized(self) -> SourceSchedulePolicy:
        """Return timezone-normalized policy for deterministic due evaluation."""
        updates: dict[str, object] = {}
        if self.last_successful_at is not None:
            updates["last_successful_at"] = _ensure_utc(self.last_successful_at)
        if self.next_eligible_at is not None:
            updates["next_eligible_at"] = _ensure_utc(self.next_eligible_at)
        if not updates:
            return self
        return self.model_copy(update=updates)


def cadence_delta(policy: SourceSchedulePolicy) -> timedelta:
    """Map cadence policy to an interval for due-state computation."""
    if policy.cadence_type == "hourly":
        return timedelta(hours=1)
    if policy.cadence_type == "daily":
        return timedelta(days=1)
    if policy.cadence_type == "weekly":
        return timedelta(weeks=1)
    if policy.cadence_type == "monthly":
        return timedelta(days=30)
    if policy.cadence_type == "custom_interval":
        value = policy.cadence_value or 1
        return timedelta(hours=value)
    raise ValueError(f"unsupported cadence_type: {policy.cadence_type}")


def resolve_due_at(*, policy: SourceSchedulePolicy, evaluated_at: datetime) -> datetime:
    """Resolve the timestamp at which the source should be considered due."""
    if policy.next_eligible_at is not None:
        return _ensure_utc(policy.next_eligible_at)
    if policy.last_successful_at is None:
        return _ensure_utc(evaluated_at)
    return _ensure_utc(policy.last_successful_at) + cadence_delta(policy)


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
