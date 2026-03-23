"""US1 integration-style tests for empty search behavior."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


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
