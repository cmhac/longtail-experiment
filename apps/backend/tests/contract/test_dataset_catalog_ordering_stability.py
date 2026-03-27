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
        options={"source_id": None, "category": None, "sort": None, "page": 1, "page_size": 20},
        group_by_source=False,
    )
    second = service.list_catalog(
        query_text=None,
        options={"source_id": None, "category": None, "sort": None, "page": 1, "page_size": 20},
        group_by_source=False,
    )

    first_ids = [item["dataset_id"] for item in first["items"]]
    second_ids = [item["dataset_id"] for item in second["items"]]

    assert first_ids == second_ids


def test_catalog_ordering_is_stable_across_page_boundaries() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    first_page = service.list_catalog(
        query_text=None,
        options={"source_id": None, "category": None, "sort": None, "page": 1, "page_size": 2},
        group_by_source=False,
    )
    second_page = service.list_catalog(
        query_text=None,
        options={"source_id": None, "category": None, "sort": None, "page": 2, "page_size": 2},
        group_by_source=False,
    )

    first_ids = [item["dataset_id"] for item in first_page["items"]]
    second_ids = [item["dataset_id"] for item in second_page["items"]]

    assert len(set(first_ids).intersection(second_ids)) == 0
    assert first_page["total_items"] == second_page["total_items"]


def test_catalog_reconciles_out_of_range_page_to_last_page() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.list_catalog(
        query_text=None,
        options={"source_id": None, "category": None, "sort": None, "page": 999, "page_size": 2},
        group_by_source=False,
    )

    assert response["total_pages"] >= 1
    assert response["page"] == response["total_pages"]
    assert response["items"]
