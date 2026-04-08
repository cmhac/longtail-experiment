"""US3 tests for directional-only transition eligibility under v2 semantics."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_lifecycle_service import TrendLifecycleService


def test_direction_available_up_is_eligible_for_notification_signal() -> None:
    direction = TrendLifecycleService.resolve_notification_direction(
        descriptor_state="available",
        direction="up",
    )

    assert direction == "up"


def test_direction_available_down_is_eligible_for_notification_signal() -> None:
    direction = TrendLifecycleService.resolve_notification_direction(
        descriptor_state="available",
        direction="down",
    )

    assert direction == "down"


def test_flat_direction_is_not_eligible_for_notification_signal() -> None:
    direction = TrendLifecycleService.resolve_notification_direction(
        descriptor_state="available",
        direction="flat",
    )

    assert direction is None


def test_unavailable_descriptor_is_not_eligible_even_with_direction_value() -> None:
    direction = TrendLifecycleService.resolve_notification_direction(
        descriptor_state="unavailable",
        direction="down",
    )

    assert direction is None


def test_missing_direction_is_not_eligible_for_notification_signal() -> None:
    direction = TrendLifecycleService.resolve_notification_direction(
        descriptor_state="available",
        direction=None,
    )

    assert direction is None
