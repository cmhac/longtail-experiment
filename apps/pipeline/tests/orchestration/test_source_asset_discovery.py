"""Foundational tests for deterministic source discovery."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.services.canonical_ingest_service import CanonicalIngestService
from src.orchestration.jobs.source_assets.discovery import (
    SourceBuilderSpec,
    discover_source_registrations,
    filter_adapter_specs,
)
from src.orchestration.jobs.source_ingest_runner import SourceIngestRunner
from src.orchestration.jobs.workflow_registry import SourceWorkflowRegistration
from src.orchestration.jobs.workflow_result import SourceWorkflowResult


class _ObservationRepository:
    def read_latest_observed_on(self, *, series_key: str):
        return None

    def upsert_observation(self, observation) -> None:
        return None


def _runner() -> SourceIngestRunner:
    return SourceIngestRunner(
        canonical_ingest_service=CanonicalIngestService(repository=_ObservationRepository())
    )


def test_discovery_returns_deterministic_source_order() -> None:
    """Default discovery should return source keys in deterministic sorted order."""
    discovered = discover_source_registrations(
        runner=_runner(),
        observation_repository=_ObservationRepository(),
    )

    source_keys = [registration.source_key for _, registration in discovered]
    assert source_keys == sorted(source_keys)


def test_discovery_order_is_stable_across_repeated_runs() -> None:
    """Repeated discovery runs should preserve source-key order exactly."""
    first = discover_source_registrations(
        runner=_runner(),
        observation_repository=_ObservationRepository(),
    )
    second = discover_source_registrations(
        runner=_runner(),
        observation_repository=_ObservationRepository(),
    )
    assert [registration.source_key for _, registration in first] == [
        registration.source_key for _, registration in second
    ]


def test_discovery_surfaces_malformed_module_failures() -> None:
    """Malformed source builders should fail fast during startup discovery."""

    def _broken_builder(runner, observation_repository):
        raise RuntimeError("module import wiring failed")

    specs = (
        SourceBuilderSpec(
            source_key="broken",
            module_name="tests.broken_source",
            title="Broken source",
            description="Broken source description",
            builder=_broken_builder,
        ),
    )

    with pytest.raises(RuntimeError, match="module import wiring failed"):
        discover_source_registrations(
            runner=_runner(),
            observation_repository=_ObservationRepository(),
            specs=specs,
        )


def test_filter_adapter_specs_ignores_non_adapter_modules() -> None:
    """Helper modules should be ignored by adapter discovery eligibility filter."""

    def _handler(request):
        return SourceWorkflowResult(source_key=request.source_key, status="success")

    def _valid_builder(runner, observation_repository):
        return SourceWorkflowRegistration(
            workflow_id="wf-valid",
            source_key="valid_source",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_handler,
        )

    def _helper_builder(runner, observation_repository):
        return SourceWorkflowRegistration(
            workflow_id="wf-helper",
            source_key="helper_module",
            owner="pipeline",
            supported_trigger_modes={"scheduled", "on_demand"},
            handler=_handler,
        )

    specs = (
        SourceBuilderSpec(
            source_key="valid_source",
            module_name="tests.valid_source",
            title="Valid source",
            description="Valid source description",
            builder=_valid_builder,
        ),
        SourceBuilderSpec(
            source_key="helper_module",
            module_name="tests.helper_module",
            title="Helper module",
            description="Helper module description",
            builder=_helper_builder,
        ),
    )

    eligible, ignored = filter_adapter_specs(specs)
    assert [spec.source_key for spec in eligible] == ["valid_source"]
    assert [spec.source_key for spec in ignored] == ["helper_module"]
