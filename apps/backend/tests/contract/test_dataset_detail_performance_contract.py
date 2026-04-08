"""Contract tests for dataset detail payload-shape invariants."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_dataset_detail_shape_invariance_contract() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    payload = service.get_dataset_detail(dataset_id="UNRATE", from_date=None, to_date=None)

    assert set(payload).issuperset(
        {
            "dataset_id",
            "source",
            "title",
            "metadata",
            "observations",
            "canonical_trend_descriptor",
            "lookback_trend_evidence",
            "has_recent_notification",
            "observation_sort",
        }
    )
    assert isinstance(payload["observations"], list)
    assert payload["observation_sort"] == "observed_on_asc,reported_at_asc"
