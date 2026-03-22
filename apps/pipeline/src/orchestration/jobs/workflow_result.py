"""Execution result schema for source workflows."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DagitFailureCategory = Literal[
    "prerequisite_missing",
    "endpoint_unavailable",
    "workspace_load_failed",
    "partial_environment",
]


def map_dagit_failure_category(
    *,
    prerequisites_ready: bool,
    endpoint_reachable: bool,
    workspace_loaded: bool,
) -> DagitFailureCategory:
    """Map startup probe state into stable local Dagit failure categories."""
    if not prerequisites_ready:
        return "prerequisite_missing"
    if not endpoint_reachable:
        return "endpoint_unavailable"
    if not workspace_loaded:
        return "workspace_load_failed"
    return "partial_environment"


class SourceWorkflowResult(BaseModel):
    """Source-scoped terminal execution result with outcome counters."""

    model_config = ConfigDict(extra="forbid")

    source_key: str = Field(min_length=1)
    status: Literal["success", "partial_success", "failure", "deferred", "not_due"]
    accepted_count: int = Field(default=0, ge=0)
    quarantined_count: int = Field(default=0, ge=0)
    failed_count: int = Field(default=0, ge=0)
    duplicate_no_op_count: int = Field(default=0, ge=0)
    conflict_count: int = Field(default=0, ge=0)
    outcome_reason_code: str | None = None
    message: str | None = None
