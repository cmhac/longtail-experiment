"""Contract tests for geography detail query behavior."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.errors import ContractQueryError
from src.query.dataset_discovery_service import DatasetDiscoveryService
from src.query.geography_detail_query import execute_geography_detail
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository

EXPECTED_US_DATASET_COUNT = 3
DETAIL_PAGE_SIZE = 2
EXPECTED_TOTAL_PAGES = 2
OUT_OF_RANGE_PAGE = 99


def _build_repository() -> InMemoryDatasetDiscoveryRepository:
    datasets, observations = build_discovery_rows()
    return InMemoryDatasetDiscoveryRepository(datasets=datasets, observations=observations)


def test_geography_detail_returns_geography_context_and_only_matching_datasets() -> None:
    """Return one geography plus only datasets attributed to that geography."""
    service = DatasetDiscoveryService(_build_repository())

    payload = execute_geography_detail(
        service,
        geography_id="us",
        page=1,
        page_size=DETAIL_PAGE_SIZE,
    ).model_dump()

    assert payload["geography"]["id"] == "us"
    assert payload["geography"]["label"] == "US"
    assert payload["geography"]["dataset_count"] == EXPECTED_US_DATASET_COUNT
    assert [item["dataset_id"] for item in payload["items"]] == ["CPIAUCSL", "GDP"]
    assert all(item["geographic_scope"] == "US" for item in payload["items"])
    assert payload["page"] == 1
    assert payload["page_size"] == DETAIL_PAGE_SIZE
    assert payload["total_items"] == EXPECTED_US_DATASET_COUNT
    assert payload["total_pages"] == EXPECTED_TOTAL_PAGES


def test_geography_detail_raises_not_found_for_unknown_geography() -> None:
    """Raise the not-found contract error for unknown geography ids."""
    service = DatasetDiscoveryService(_build_repository())

    with pytest.raises(ContractQueryError, match="geography_not_found"):
        execute_geography_detail(service, geography_id="unknown-geography", page=1, page_size=20)


def test_geography_detail_reconciles_out_of_range_page_to_last_page() -> None:
    """Reconcile out-of-range geography page requests to the last valid page."""
    service = DatasetDiscoveryService(_build_repository())

    payload = execute_geography_detail(
        service,
        geography_id="us",
        page=OUT_OF_RANGE_PAGE,
        page_size=1,
    ).model_dump()

    assert payload["page"] == payload["total_pages"]
    assert payload["items"]
