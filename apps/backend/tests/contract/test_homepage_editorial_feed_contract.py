"""Contract tests for homepage editorial recent feed payload."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_recent_items_include_editorial_optional_fields_and_actions() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    payload = service.list_recent_updates(limit=5)

    first_item = payload["items"][0]
    assert "description" in first_item
    assert "geographic_scope" in first_item
    assert first_item["action_links"]["view_table_href"].startswith("/datasets/")
    assert first_item["action_links"]["download_csv_href"].startswith("/api/datasets/")


def test_recent_actions_encode_dataset_identifier() -> None:
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=[
            {
                "dataset_id": "ID WITH SPACE",
                "source": {"id": "fred", "name": "FRED"},
                "title": "Dataset With Space",
                "description": None,
                "geographic_scope": "US",
                "topic_tags": [],
            }
        ],
        observations=[
            {
                "dataset_id": "ID WITH SPACE",
                "observed_on": "2026-02-01",
                "value": 1.0,
                "reported_at": "2026-02-10T00:00:00Z",
                "attributes": {},
            }
        ],
    )
    service = DatasetDiscoveryService(repository)

    payload = service.list_recent_updates(limit=5)

    assert payload["items"][0]["action_links"]["view_table_href"] == "/datasets/ID%20WITH%20SPACE"
    assert (
        payload["items"][0]["action_links"]["download_csv_href"]
        == "/api/datasets/ID%20WITH%20SPACE.csv"
    )
