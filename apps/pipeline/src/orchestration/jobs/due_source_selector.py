"""Determine due-source eligibility for scheduled and on-demand runs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from .source_schedule_policy import SourceSchedulePolicy, resolve_due_at
from .workflow_registry import SourceWorkflowRegistration


@dataclass(frozen=True)
class SourceEligibilityDecision:
    """Eligibility decision snapshot for one source in one run."""

    source_key: str
    eligibility_state: str
    reason_code: str
    evaluated_at: datetime
    due_at: datetime | None
    selected_for_execution: bool


class DueSourceSelector:
    """Evaluate source schedule policies and produce deterministic due ordering."""

    def evaluate_scheduled(
        self,
        *,
        registrations: list[SourceWorkflowRegistration],
        evaluated_at: datetime,
    ) -> list[SourceEligibilityDecision]:
        """Evaluate all registrations for scheduled trigger eligibility."""
        now = _ensure_utc(evaluated_at)
        decisions: list[SourceEligibilityDecision] = []
        due_pool: list[tuple[datetime, str]] = []

        by_source = sorted(registrations, key=lambda registration: registration.source_key)
        for registration in by_source:
            policy = registration.schedule_policy
            if policy is None:
                policy = SourceSchedulePolicy(
                    source_key=registration.source_key,
                    cadence_type="hourly",
                )

            normalized = policy.normalized()
            if not normalized.is_active:
                decisions.append(
                    SourceEligibilityDecision(
                        source_key=registration.source_key,
                        eligibility_state="skipped_inactive",
                        reason_code="source_inactive",
                        evaluated_at=now,
                        due_at=None,
                        selected_for_execution=False,
                    )
                )
                continue

            try:
                due_at = resolve_due_at(policy=normalized, evaluated_at=now)
            except Exception:
                decisions.append(
                    SourceEligibilityDecision(
                        source_key=registration.source_key,
                        eligibility_state="skipped_invalid_policy",
                        reason_code="invalid_policy",
                        evaluated_at=now,
                        due_at=None,
                        selected_for_execution=False,
                    )
                )
                continue

            if due_at <= now:
                due_pool.append((due_at, registration.source_key))
                decisions.append(
                    SourceEligibilityDecision(
                        source_key=registration.source_key,
                        eligibility_state="due",
                        reason_code="due_for_execution",
                        evaluated_at=now,
                        due_at=due_at,
                        selected_for_execution=True,
                    )
                )
                continue

            decisions.append(
                SourceEligibilityDecision(
                    source_key=registration.source_key,
                    eligibility_state="not_due",
                    reason_code="cadence_not_due",
                    evaluated_at=now,
                    due_at=due_at,
                    selected_for_execution=False,
                )
            )

        ranked_due = sorted(due_pool, key=lambda item: (item[0], item[1]))
        due_rank = {key: index for index, (_due_at, key) in enumerate(ranked_due)}

        # Keep non-due/skipped states stable while preserving strict FIFO due ordering.
        return sorted(
            decisions,
            key=lambda decision: (
                0 if decision.eligibility_state == "due" else 1,
                due_rank.get(decision.source_key, 10_000),
                decision.source_key,
            ),
        )

    def evaluate_on_demand(
        self,
        *,
        source_keys: list[str],
        evaluated_at: datetime,
    ) -> list[SourceEligibilityDecision]:
        """Create eligibility snapshots for explicit on-demand source selections."""
        now = _ensure_utc(evaluated_at)
        return [
            SourceEligibilityDecision(
                source_key=source_key,
                eligibility_state="due",
                reason_code="on_demand_selected",
                evaluated_at=now,
                due_at=now,
                selected_for_execution=True,
            )
            for source_key in sorted(source_keys)
        ]


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
