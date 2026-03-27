"""US1 integration-style tests for empty search behavior."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository

DEFAULT_SEARCH_PAGE_SIZE = 20


def test_empty_search_uses_default_context() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.search_datasets(query_text="   ", page=1, page_size=10)

    assert response["total_items"] == len(datasets)
    assert response["items"]
    assert response["sort"] == "latest_update_at_desc,title_asc,dataset_id_asc"


def test_search_defaults_page_size_and_page_for_blank_query() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.search_datasets(query_text="", page=None, page_size=None)

    assert response["page"] == 1
    assert response["page_size"] == DEFAULT_SEARCH_PAGE_SIZE
    assert response["total_items"] == len(datasets)


def test_search_filtered_scope_retains_pagination_metadata() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.search_datasets(query_text="inflation", page=1, page_size=1)

    assert response["page"] == 1
    assert response["page_size"] == 1
    assert response["total_items"] >= 1
    assert response["total_pages"] >= 1
    assert all("inflation" in item["topic_tags"] for item in response["items"])


def test_search_reconciles_out_of_range_page_to_last_page() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.search_datasets(query_text=None, page=999, page_size=2)

    assert response["total_pages"] >= 1
    assert response["page"] == response["total_pages"]
    assert response["items"]
