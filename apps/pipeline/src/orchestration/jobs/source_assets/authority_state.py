"""Scheduling authority state for post-cutover runtime behavior."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

AuthorityMode = Literal["dagster_only", "transitional"]


@dataclass(frozen=True)
class SchedulingAuthorityState:
    """Runtime authority mode for scheduling and recovery behavior."""

    authority_mode: AuthorityMode
    legacy_paths_disabled: bool
    partial_failure_mode: bool
    cutover_completed_at: datetime | None


def dagster_only_authority_state(*, partial_failure_mode: bool = False) -> SchedulingAuthorityState:
    """Build default post-cutover authority state where Dagster is the sole scheduler."""
    return SchedulingAuthorityState(
        authority_mode="dagster_only",
        legacy_paths_disabled=True,
        partial_failure_mode=partial_failure_mode,
        cutover_completed_at=datetime.now(tz=UTC),
    )


def assert_dagster_only_authority(state: SchedulingAuthorityState) -> None:
    """Guard legacy scheduler paths once cutover is active."""
    if state.authority_mode != "dagster_only":
        raise RuntimeError("scheduling authority must be dagster_only after cutover")
    if not state.legacy_paths_disabled:
        raise RuntimeError("legacy scheduler paths must remain disabled after cutover")
    if state.cutover_completed_at is None:
        raise RuntimeError("cutover timestamp is required in dagster_only mode")
