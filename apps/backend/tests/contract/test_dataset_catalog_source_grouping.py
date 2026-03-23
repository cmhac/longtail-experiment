"""US2 contract tests for source grouping and filtering behavior."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_catalog_source_filter_and_search_are_composable() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.list_catalog(
        query_text="consumer",
        source_id="fred",
        page=1,
        page_size=20,
        group_by_source=False,
    )

    assert [item["dataset_id"] for item in response["items"]] == ["CPIAUCSL"]


def test_catalog_grouping_returns_source_buckets() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.list_catalog(
        query_text=None,
        source_id=None,
        page=1,
        page_size=20,
        group_by_source=True,
    )

    assert response["groups"]
    assert all("dataset_count" in group for group in response["groups"])
