"""Outcome metadata helpers for source-level operator visibility."""

from __future__ import annotations

from ..workflow_result import SourceWorkflowResult


def build_failure_summary(result: SourceWorkflowResult) -> str | None:
    """Build a short source failure summary for operator triage."""
    if result.status != "failure":
        return None
    reason = result.outcome_reason_code or "unknown_failure"
    message = result.message or "no failure message"
    return f"{reason}: {message}"
