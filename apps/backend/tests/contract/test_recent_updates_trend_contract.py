"""US2 contract tests for trend events in unified recent updates payload."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from src.query.dataset_recent_updates_query import execute_recent_updates
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_recent_updates_contract_accepts_trend_event_items() -> None:
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

    assert any(item["item_type"] == "trend_event" for item in response["items"])
