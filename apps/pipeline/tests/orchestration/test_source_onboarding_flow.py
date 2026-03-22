"""Integration test for source onboarding flow."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Protocol

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.services.canonical_ingest_service import CanonicalIngestService
from src.orchestration.jobs.source_ingest_runner import SourceIngestRunner
from src.orchestration.jobs.sources.example_source import build_example_source_workflow
from src.orchestration.jobs.workflow_registry import SourceWorkflowRegistry


class _Observation(Protocol):
    series_key: object
    observed_on: object
    value: object


class _ObservationRepository:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def upsert_observation(self, observation: _Observation) -> None:
        self.rows.append(
            {
                "series_key": str(observation.series_key),
                "observed_on": observation.observed_on,
                "value": observation.value,
            }
        )


def test_onboarded_source_can_ingest_valid_and_quarantine_invalid_rows() -> None:
    """Onboarded source should process valid rows and quarantine invalid rows."""
    repo = _ObservationRepository()
    canonical_service = CanonicalIngestService(repository=repo)
    runner = SourceIngestRunner(canonical_ingest_service=canonical_service)
    registry = SourceWorkflowRegistry()
    registry.register(build_example_source_workflow(runner))

    request: dict[str, object] = {
        "records": [
            {
                "source_name": "BLS",
                "source_type": "external",
                "series_key": "CPI.US.ALL",
                "metric_name": "Consumer Price Index",
                "frequency": "monthly",
                "date": "2026-01-01",
                "reported_at": "2026-02-01T00:00:00Z",
                "value": "302.5",
            },
            {
                "source_type": "external",
                "series_key": "BROKEN",
                "metric_name": "Broken",
                "frequency": "monthly",
                "date": "2026-01-01",
                "reported_at": "2026-02-01T00:00:00Z",
                "value": "0",
            },
        ]
    }

    result = registry.execute_for_source(
        source_key="example_source",
        run_id="run-1",
        trigger_type="on_demand",
        run_context=request,
    )

    assert result.accepted_count == 1
    assert result.quarantined_count == 1
    assert result.status == "partial_success"
