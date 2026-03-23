"""US3 contract tests for dataset detail payload behavior."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_detail_returns_metadata_and_observations() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = service.get_dataset_detail(
        dataset_id="UNRATE",
        from_date=None,
        to_date=None,
    )

    assert response["dataset_id"] == "UNRATE"
    assert response["title"] == "Unemployment Rate"
    assert response["observations"]
    assert response["observation_sort"] == "observed_on_asc,reported_at_asc"
