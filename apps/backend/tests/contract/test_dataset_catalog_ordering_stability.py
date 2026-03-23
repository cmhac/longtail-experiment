"""US2 integration-style tests for deterministic catalog ordering."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_catalog_ordering_is_stable_for_repeated_requests() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    first = service.list_catalog(
        query_text=None,
        source_id=None,
        page=1,
        page_size=20,
        group_by_source=False,
    )
    second = service.list_catalog(
        query_text=None,
        source_id=None,
        page=1,
        page_size=20,
        group_by_source=False,
    )

    first_ids = [item["dataset_id"] for item in first["items"]]
    second_ids = [item["dataset_id"] for item in second["items"]]

    assert first_ids == second_ids
