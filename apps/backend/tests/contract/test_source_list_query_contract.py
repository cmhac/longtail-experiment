"""Contract tests for source list query behavior."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from src.query.source_list_query import execute_source_list
from tests.fixtures.source_discovery_repository import build_source_discovery_repository

EXPECTED_SOURCE_COUNT = 2
EXPECTED_FRED_DATASET_COUNT = 2


def test_source_list_returns_unique_sources_with_counts() -> None:
    """Return one summary row per discoverable source."""
    service = DatasetDiscoveryService(build_source_discovery_repository())

    payload = execute_source_list(service).model_dump()

    assert payload["total_items"] == EXPECTED_SOURCE_COUNT
    assert payload["items"][0]["id"] == "bea"
    assert payload["items"][0]["title"] == "BEA"
    assert payload["items"][0]["description"] == (
        "US national accounts published by the Bureau of Economic Analysis."
    )
    assert payload["items"][0]["dataset_count"] == 1
    assert payload["items"][1]["id"] == "fred"
    assert payload["items"][1]["title"] == "FRED"
    assert payload["items"][1]["description"] == (
        "Federal Reserve Economic Data from the St. Louis Fed."
    )
    assert payload["items"][1]["dataset_count"] == EXPECTED_FRED_DATASET_COUNT
    assert payload["sort"] == "source_title_asc,source_id_asc"
