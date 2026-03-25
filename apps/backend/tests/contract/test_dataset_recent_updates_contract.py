"""US1 contract tests for recent updates behavior."""

# ruff: noqa: D103, PLR2004

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_recent_updates_returns_maximum_five_rows() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.list_recent_updates(limit=5)

    assert len(response["items"]) <= 5
    assert response["limit"] == 5


def test_recent_updates_orders_by_latest_update_descending() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.list_recent_updates(limit=5)
    latest_values = [item.get("latest_update_at") or "" for item in response["items"]]

    assert latest_values == sorted(latest_values, reverse=True)


def test_recent_updates_include_action_links_per_item() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.list_recent_updates(limit=5)

    first_item = response["items"][0]
    assert first_item["action_links"]["view_table_href"].startswith("/datasets/")
    assert first_item["action_links"]["download_csv_href"].startswith("/api/datasets/")
