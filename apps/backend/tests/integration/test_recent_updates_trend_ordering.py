"""US2 integration test for unified recent feed trend ordering."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from src.query.dataset_recent_updates_query import execute_recent_updates
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_unified_recent_feed_orders_by_event_timestamp_with_trends() -> None:
    """Unified feed should intermix trend and dataset rows sorted by event timestamp."""
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
        trend_events=[
            {
                "dataset_id": "UNRATE",
                "source": {"id": "bls", "name": "BLS"},
                "title": "Unemployment Trend",
                "direction": "down",
                "confidence_score": 0.64,
                "start_period": "2026-03-01",
            }
        ],
    )
    service = DatasetDiscoveryService(repository)

    response = execute_recent_updates(service, limit=5).model_dump()

    assert response["items"][0]["latest_update_at"] >= response["items"][-1]["latest_update_at"]
    assert any(item["item_type"] == "dataset_update" for item in response["items"])
    assert any(item["item_type"] == "trend_event" for item in response["items"])
