"""US1 contract tests for landing search behavior."""

# ruff: noqa: D103, PLR2004

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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
    assert response["sort"] == "latest_update_at_desc,title_asc,dataset_id_asc"
