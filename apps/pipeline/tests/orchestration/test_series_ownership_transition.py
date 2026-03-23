"""US3 ownership transition and duplicate-guard tests."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.due_source_selector import DueSourceSelector
from src.orchestration.jobs.parallel_source_executor import ParallelSourceExecutor
from src.orchestration.jobs.run_coordinator import RunCoordinator
from src.orchestration.jobs.source_assets.ownership_mode import (
    OwnershipMode,
    SeriesOwnershipModeRecord,
)
from src.orchestration.jobs.source_assets.ownership_transition import (
    apply_ownership_transition,
)
from src.orchestration.jobs.source_assets.series_catalog import SeriesCatalogEntry
from src.orchestration.jobs.workflow_registry import (
    SourceWorkflowRegistration,
    SourceWorkflowRegistry,
)
from src.orchestration.jobs.workflow_result import SourceWorkflowResult
from src.orchestration.resources.source_lock_service import SourceLockService

TWO = 2


def test_apply_ownership_transition_closes_prior_window() -> None:
    """Ownership transition should close previous active record at transition boundary."""
    records = [
        SeriesOwnershipModeRecord(
            series_item_key="fred_gasregw",
            owner_adapter_key="fred_fedfunds",
            mode="grouped",
            effective_from=datetime(2026, 1, 1, tzinfo=UTC),
            effective_to=None,
        )
    ]

    updated = apply_ownership_transition(
        existing_records=records,
        series_item_key="fred_gasregw",
        new_owner_adapter_key="fred_gasregw",
        new_mode="split",
        effective_from=datetime(2026, 2, 1, tzinfo=UTC),
    )

    assert len(updated) == TWO
    grouped = next(record for record in updated if record.owner_adapter_key == "fred_fedfunds")
    split = next(record for record in updated if record.owner_adapter_key == "fred_gasregw")
    assert grouped.effective_to == datetime(2026, 2, 1, tzinfo=UTC)
    assert split.effective_to is None


def test_apply_ownership_transition_rejects_invalid_mode() -> None:
    """Ownership transition should reject unsupported mode declarations."""
    with pytest.raises(ValueError, match="grouped or split"):
        apply_ownership_transition(
            existing_records=[],
            series_item_key="fred_gasregw",
            new_owner_adapter_key="fred_gasregw",
            new_mode=cast(OwnershipMode, "invalid"),
            effective_from=datetime(2026, 2, 1, tzinfo=UTC),
        )


def test_transition_guard_prevents_duplicate_scheduled_execution() -> None:
    """Scheduled execution should run only the authoritative owner in coexistence mode."""
    registry = SourceWorkflowRegistry()

    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-grouped",
            source_key="fred_fedfunds",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=lambda request: SourceWorkflowResult(
                source_key=request.source_key,
                status="success",
                accepted_count=1,
            ),
        )
    )
    registry.register(
        SourceWorkflowRegistration(
            workflow_id="wf-split",
            source_key="fred_gasregw",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=lambda request: SourceWorkflowResult(
                source_key=request.source_key,
                status="success",
                accepted_count=1,
            ),
        )
    )

    coordinator = RunCoordinator(
        workflow_registry=registry,
        source_lock_service=SourceLockService(),
        due_source_selector=DueSourceSelector(),
        parallel_source_executor=ParallelSourceExecutor(max_active_sources=2),
        series_catalog_entries=(
            SeriesCatalogEntry(
                source_key="fred_fedfunds",
                provider_group_key="fred",
                series_item_key="fred_gasregw",
                canonical_series_key="ENERGY.US.GASREGW",
                ownership_mode="grouped",
            ),
            SeriesCatalogEntry(
                source_key="fred_gasregw",
                provider_group_key="fred",
                series_item_key="fred_gasregw",
                canonical_series_key="ENERGY.US.GASREGW",
                ownership_mode="split",
            ),
        ),
        ownership_mode_registry={
            "fred_gasregw": SeriesOwnershipModeRecord(
                series_item_key="fred_gasregw",
                owner_adapter_key="fred_gasregw",
                mode="split",
            )
        },
    )

    result = coordinator.run(trigger_type="scheduled", requested_by="scheduler")
    source_keys = [row["source_key"] for row in result["source_results"]]
    assert source_keys == ["fred_gasregw"]
