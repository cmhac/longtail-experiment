"""Foundational tests for source schedule policy and due selection behavior."""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.due_source_selector import DueSourceSelector
from src.orchestration.jobs.source_schedule_policy import SourceSchedulePolicy
from src.orchestration.jobs.workflow_registry import SourceWorkflowRegistration
from src.orchestration.jobs.workflow_result import SourceWorkflowResult


def _build_registration(
    source_key: str,
    *,
    policy: SourceSchedulePolicy,
) -> SourceWorkflowRegistration:
    def _handler(_request):
        return SourceWorkflowResult(source_key=source_key, status="success", accepted_count=1)

    return SourceWorkflowRegistration(
        workflow_id=f"wf-{source_key}",
        source_key=source_key,
        owner="pipeline",
        supported_trigger_modes={"scheduled", "on_demand"},
        handler=_handler,
        schedule_policy=policy,
    )


def test_custom_interval_requires_value() -> None:
    """Custom cadence policies should require cadence_value."""
    with pytest.raises(ValueError):
        SourceSchedulePolicy(source_key="bls", cadence_type="custom_interval")


def test_next_eligible_must_not_precede_last_success() -> None:
    """Policy validator should reject backwards eligibility timestamps."""
    with pytest.raises(ValueError):
        SourceSchedulePolicy(
            source_key="bls",
            cadence_type="hourly",
            last_successful_at=datetime(2026, 3, 20, 12, 0, tzinfo=UTC),
            next_eligible_at=datetime(2026, 3, 20, 11, 0, tzinfo=UTC),
        )


def test_due_selector_uses_earliest_due_fifo_order() -> None:
    """Due source ordering should remain strict FIFO by earliest due timestamp."""
    now = datetime(2026, 3, 21, 12, 0, tzinfo=UTC)
    selector = DueSourceSelector()

    registrations = [
        _build_registration(
            "source-a",
            policy=SourceSchedulePolicy(
                source_key="source-a",
                cadence_type="hourly",
                last_successful_at=now - timedelta(hours=2),
            ),
        ),
        _build_registration(
            "source-b",
            policy=SourceSchedulePolicy(
                source_key="source-b",
                cadence_type="hourly",
                last_successful_at=now - timedelta(hours=3),
            ),
        ),
        _build_registration(
            "source-c",
            policy=SourceSchedulePolicy(
                source_key="source-c",
                cadence_type="daily",
                last_successful_at=now,
            ),
        ),
    ]

    decisions = selector.evaluate_scheduled(registrations=registrations, evaluated_at=now)

    due_decisions = [decision for decision in decisions if decision.eligibility_state == "due"]
    assert [decision.source_key for decision in due_decisions] == ["source-b", "source-a"]

    not_due = [decision for decision in decisions if decision.eligibility_state == "not_due"]
    assert len(not_due) == 1
    assert not_due[0].source_key == "source-c"
