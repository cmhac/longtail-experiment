"""Contract tests for homepage search summary response shape."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from src.query.dataset_search_summary_query import execute_search_summary
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_search_summary_returns_non_negative_aggregate_counts() -> None:
    datasets, observations = build_discovery_rows()
    service = DatasetDiscoveryService(
        InMemoryDatasetDiscoveryRepository(datasets=datasets, observations=observations)
    )

    payload = execute_search_summary(service).model_dump()

    assert payload["active_dataset_count"] >= 0
    assert payload["active_source_count"] >= 0
    assert payload["active_dataset_count"] == len(datasets)
    assert payload["generated_at"] is not None
