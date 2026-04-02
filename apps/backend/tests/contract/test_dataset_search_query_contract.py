"""US1 contract tests for landing search behavior."""

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


def test_search_matches_metadata_and_topic_tags() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.search_datasets(query_text="labor", page=1, page_size=20)
    dataset_ids = [item["dataset_id"] for item in response["items"]]

    assert dataset_ids == ["UNRATE"]
    assert response["items"][0]["canonical_trend_descriptor"]["descriptor_state"] in {
        "available",
        "unavailable",
    }


def test_search_response_includes_pagination_and_sort_metadata() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.search_datasets(query_text="us", page=1, page_size=2)

    assert response["page"] == 1
    assert response["page_size"] == 2
    assert response["total_items"] >= 1
    assert response["total_pages"] >= 1
    assert response["sort"] == "latest_update_at_desc,title_asc,dataset_id_asc"


def test_search_defaults_page_and_page_size_when_not_provided() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.search_datasets(query_text=None, page=None, page_size=None)

    assert response["page"] == 1
    assert response["page_size"] == 20
    assert response["total_items"] == len(datasets)
    assert response["total_pages"] >= 1


def test_search_rejects_out_of_bounds_page_inputs() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    with pytest.raises(ContractQueryError, match="page must be greater than or equal to 1"):
        service.search_datasets(query_text=None, page=0, page_size=20)

    with pytest.raises(ContractQueryError, match="page_size must be between 1 and 100"):
        service.search_datasets(query_text=None, page=1, page_size=101)
