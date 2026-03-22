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
)
from src.orchestration.jobs.source_ingest_runner import SourceIngestRunner


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
    assert source_keys == [
        "dummy_source",
        "example_source",
        "fred_fedfunds",
        "implementation_window_source",
    ]


def test_discovery_surfaces_malformed_module_failures() -> None:
    """Malformed source builders should fail fast during startup discovery."""

    def _broken_builder(runner, observation_repository):
        raise RuntimeError("module import wiring failed")

    specs = (
        SourceBuilderSpec(
            source_key="broken",
            module_name="tests.broken_source",
            builder=_broken_builder,
        ),
    )

    with pytest.raises(RuntimeError, match="module import wiring failed"):
        discover_source_registrations(
            runner=_runner(),
            observation_repository=_ObservationRepository(),
            specs=specs,
        )
