"""US2 contract tests for dataset catalog listing behavior."""

# ruff: noqa: D103, PLR2004

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.errors import ContractQueryError
from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_catalog_returns_paging_metadata() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.list_catalog(
        query_text=None,
        options={"source_id": None, "category": None, "sort": None, "page": 1, "page_size": 2},
        group_by_source=False,
    )

    assert response["page"] == 1
    assert response["page_size"] == 2
    assert response["total_items"] == len(datasets)
    assert response["total_pages"] == ((len(datasets) - 1) // 2 + 1)
    assert response["aggregations"]["total_dataset_count"] == len(datasets)
    assert response["sort"] == "latest_update_at_desc,title_asc,dataset_id_asc"


def test_catalog_items_include_source_attribution() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.list_catalog(
        query_text="us",
        options={
            "source_id": None,
            "category": None,
            "sort": None,
            "page": 1,
            "page_size": 20,
        },
        group_by_source=False,
    )

    assert response["items"]
    assert all("source" in item for item in response["items"])


def test_catalog_applies_server_side_category_filter_and_title_sort() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.list_catalog(
        query_text=None,
        options={
            "source_id": None,
            "category": "prices",
            "sort": "title_asc",
            "page": 1,
            "page_size": 20,
        },
        group_by_source=False,
    )

    assert response["items"]
    assert all("prices" in item["topic_tags"] for item in response["items"])
    assert response["sort"] == "title_asc,dataset_id_asc"


def test_catalog_defaults_page_and_page_size_when_not_provided() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.list_catalog(
        query_text=None,
        options={
            "source_id": None,
            "category": None,
            "sort": None,
        },
        group_by_source=False,
    )

    assert response["page"] == 1
    assert response["page_size"] == 20
    assert response["total_items"] == len(datasets)


def test_catalog_rejects_out_of_bounds_page_inputs() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    with pytest.raises(ContractQueryError, match="page must be greater than or equal to 1"):
        service.list_catalog(
            query_text=None,
            options={"source_id": None, "category": None, "sort": None, "page": 0},
            group_by_source=False,
        )

    with pytest.raises(ContractQueryError, match="page_size must be between 1 and 100"):
        service.list_catalog(
            query_text=None,
            options={
                "source_id": None,
                "category": None,
                "sort": None,
                "page": 1,
                "page_size": 101,
            },
            group_by_source=False,
        )
