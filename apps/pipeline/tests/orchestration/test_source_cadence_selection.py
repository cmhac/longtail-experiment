"""US2 cadence eligibility selection tests."""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.due_source_selector import DueSourceSelector
from src.orchestration.jobs.source_schedule_policy import SourceSchedulePolicy
from src.orchestration.jobs.workflow_registry import SourceWorkflowRegistration
from src.orchestration.jobs.workflow_result import SourceWorkflowResult
from src.orchestration.schedules.source_asset_schedules import SOURCE_CADENCE_DEFINITIONS


def _registration(
    source_key: str,
    *,
    schedule_policy: SourceSchedulePolicy,
) -> SourceWorkflowRegistration:
    def _handler(_request):
        return SourceWorkflowResult(source_key=source_key, status="success", accepted_count=1)

    return SourceWorkflowRegistration(
        workflow_id=f"wf-{source_key}",
        source_key=source_key,
        owner="pipeline",
        supported_trigger_modes={"scheduled", "on_demand"},
        handler=_handler,
        schedule_policy=schedule_policy,
    )


def test_due_not_due_selection_across_cadence_types() -> None:
    """Selector should return due and not-due states for mixed cadence policies."""
    now = datetime(2026, 3, 21, 12, 0, tzinfo=UTC)
    selector = DueSourceSelector()

    registrations = [
        _registration(
            "hourly-source",
            schedule_policy=SourceSchedulePolicy(
                source_key="hourly-source",
                cadence_type="hourly",
                last_successful_at=now - timedelta(hours=2),
            ),
        ),
        _registration(
            "daily-source",
            schedule_policy=SourceSchedulePolicy(
                source_key="daily-source",
                cadence_type="daily",
                last_successful_at=now - timedelta(hours=6),
            ),
        ),
        _registration(
            "weekly-source",
            schedule_policy=SourceSchedulePolicy(
                source_key="weekly-source",
                cadence_type="weekly",
                last_successful_at=now - timedelta(days=8),
            ),
        ),
        _registration(
            "monthly-source",
            schedule_policy=SourceSchedulePolicy(
                source_key="monthly-source",
                cadence_type="monthly",
                last_successful_at=now - timedelta(days=10),
            ),
        ),
    ]

    decisions = selector.evaluate_scheduled(registrations=registrations, evaluated_at=now)
    by_source = {decision.source_key: decision for decision in decisions}

    assert by_source["hourly-source"].eligibility_state == "due"
    assert by_source["weekly-source"].eligibility_state == "due"
    assert by_source["daily-source"].eligibility_state == "not_due"
    assert by_source["monthly-source"].eligibility_state == "not_due"


def test_invalid_policy_is_marked_as_skipped_invalid_policy() -> None:
    """Malformed cadence metadata should be surfaced as skipped_invalid_policy."""
    now = datetime(2026, 3, 21, 12, 0, tzinfo=UTC)
    selector = DueSourceSelector()

    malformed_policy = SourceSchedulePolicy.model_construct(
        source_key="invalid-source",
        cadence_type="broken_cadence",
        cadence_value=None,
        timezone="UTC",
        is_active=True,
        last_successful_at=now,
        next_eligible_at=None,
        priority_class="normal",
    )

    decisions = selector.evaluate_scheduled(
        registrations=[_registration("invalid-source", schedule_policy=malformed_policy)],
        evaluated_at=now,
    )

    assert decisions[0].eligibility_state == "skipped_invalid_policy"
    assert decisions[0].reason_code == "invalid_policy"
    assert decisions[0].selected_for_execution is False


def test_source_asset_owns_schedule_cadence() -> None:
    """Feature 011 US1: each source schedule definition maps to its own cadence."""
    assert "dummy_source" in SOURCE_CADENCE_DEFINITIONS
    assert "example_source" in SOURCE_CADENCE_DEFINITIONS
    assert "fred_fedfunds" in SOURCE_CADENCE_DEFINITIONS

    assert SOURCE_CADENCE_DEFINITIONS["dummy_source"][1] == "hourly"
    assert SOURCE_CADENCE_DEFINITIONS["example_source"][1] == "daily"
    assert SOURCE_CADENCE_DEFINITIONS["fred_fedfunds"][1] == "daily"


def test_source_asset_schedules_have_distinct_cron_definitions() -> None:
    """Feature 011 US1: per-source schedules should have appropriate cron expressions."""
    # Hourly: every hour on the hour
    assert SOURCE_CADENCE_DEFINITIONS["dummy_source"][0] == "0 * * * *"
    # Daily: midnight
    assert SOURCE_CADENCE_DEFINITIONS["example_source"][0] == "0 0 * * *"
    assert SOURCE_CADENCE_DEFINITIONS["fred_fedfunds"][0] == "0 0 * * *"
