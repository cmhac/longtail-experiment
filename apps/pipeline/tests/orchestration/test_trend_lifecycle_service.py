"""Tests for trend lifecycle notification visibility classification."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.trend_lifecycle_service import TrendLifecycleService


def test_classify_notification_visibility_for_incremental_runs() -> None:
    processing_context, visibility = TrendLifecycleService.classify_notification_visibility(
        run_full_backfill=False,
    )

    assert processing_context == "incremental"
    assert visibility == "user_visible"


def test_classify_notification_visibility_for_backfill_runs() -> None:
    processing_context, visibility = TrendLifecycleService.classify_notification_visibility(
        run_full_backfill=True,
    )

    assert processing_context == "historical_reprocessing"
    assert visibility == "audit_only"
