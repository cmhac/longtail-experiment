"""Regression guards for adjacent discovery endpoint behavior."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_adjacent_discovery_endpoints_remain_functional() -> None:
    datasets, observations = build_discovery_rows()
    service = DatasetDiscoveryService(
        InMemoryDatasetDiscoveryRepository(datasets=datasets, observations=observations)
    )

    search_payload = service.search_datasets(query_text="rate", page=1, page_size=10)
    catalog_payload = service.list_catalog(
        query_text=None, options={"page": 1, "page_size": 10}, group_by_source=False
    )
    sources_payload = service.list_sources()

    assert search_payload["items"]
    assert catalog_payload["items"]
    assert sources_payload["items"]
