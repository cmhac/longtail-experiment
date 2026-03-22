"""Execution request schema for source workflows."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class SourceWorkflowRequest(BaseModel):
    """Normalized request payload passed to source workflow handlers."""

    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1)
    source_key: str = Field(min_length=1)
    trigger_type: Literal["scheduled", "on_demand"]
    requested_at: datetime | None = None
    requested_by: str | None = None
    run_context: dict[str, Any] = Field(default_factory=dict)
