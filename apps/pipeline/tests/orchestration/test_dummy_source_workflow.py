"""Contract tests for dummy source workflow behavior."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Protocol

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.services.canonical_ingest_service import CanonicalIngestService
from src.orchestration.jobs.source_ingest_runner import SourceIngestRunner
from src.orchestration.jobs.sources.dummy_source import (
    DUMMY_SOURCE_KEY,
    DummySourceProvider,
    build_dummy_source_workflow,
)
from src.orchestration.jobs.workflow_registry import SourceWorkflowRegistry


class _Observation(Protocol):
    series_key: object


class _CaptureRepository:
    def __init__(self) -> None:
        self.rows: list[_Observation] = []

    def upsert_observation(self, observation: _Observation) -> None:
        self.rows.append(observation)


def test_dummy_source_workflow_ingests_provider_records() -> None:
    """Dummy source should ingest provider payloads as accepted observations."""
    repo = _CaptureRepository()
    service = CanonicalIngestService(repository=repo)
    runner = SourceIngestRunner(canonical_ingest_service=service)

    registry = SourceWorkflowRegistry()
    registry.register(build_dummy_source_workflow(runner, provider=DummySourceProvider()))

    result = registry.execute_for_source(
        source_key=DUMMY_SOURCE_KEY,
        run_id="run-dummy",
        trigger_type="on_demand",
        run_context={},
    )

    assert result.status == "success"
    assert result.accepted_count == 1
    assert len(repo.rows) == 1
    assert str(repo.rows[0].series_key) == "DUMMY.US.CPI"
