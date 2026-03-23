"""US3 integration-style tests for observation ordering semantics."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_detail_observations_are_chronological() -> None:
    datasets, observations = build_discovery_rows()
    observations.append(
        {
            "dataset_id": "UNRATE",
            "observed_on": "2025-12-01",
            "value": 3.9,
            "reported_at": "2026-01-01T00:00:00Z",
            "attributes": {"revision": 0},
        }
    )
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

    observed_values = [item["observed_on"] for item in response["observations"]]
    assert observed_values == sorted(observed_values)
