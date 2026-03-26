"""Helpers for source discovery contract tests."""

from __future__ import annotations

from .dataset_discovery_factory import build_discovery_rows
from .dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def build_source_discovery_repository() -> InMemoryDatasetDiscoveryRepository:
    """Return a fixture repository populated with source-attributed discovery data."""
    datasets, observations = build_discovery_rows()
    return InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
