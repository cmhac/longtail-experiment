"""Contract tests for topic detail query behavior."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.errors import ContractQueryError
from src.query.dataset_discovery_service import DatasetDiscoveryService
from src.query.topic_detail_query import execute_topic_detail
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def _build_repository() -> InMemoryDatasetDiscoveryRepository:
    datasets, observations = build_discovery_rows()
    return InMemoryDatasetDiscoveryRepository(datasets=datasets, observations=observations)


def test_topic_detail_returns_topic_context_and_only_matching_datasets() -> None:
    """Return one topic plus only datasets attributed to that topic."""
    service = DatasetDiscoveryService(_build_repository())

    payload = execute_topic_detail(service, topic_id="inflation", page=1, page_size=1).model_dump()

    assert payload["topic"]["id"] == "inflation"
    assert payload["topic"]["label"] == "inflation"
    assert payload["topic"]["dataset_count"] == 1
    assert [item["dataset_id"] for item in payload["items"]] == ["CPIAUCSL"]
    assert all("inflation" in item["topic_tags"] for item in payload["items"])
    assert payload["page"] == 1
    assert payload["page_size"] == 1
    assert payload["total_items"] == 1
    assert payload["total_pages"] == 1


def test_topic_detail_raises_not_found_for_unknown_topic() -> None:
    """Raise the not-found contract error for unknown topic ids."""
    service = DatasetDiscoveryService(_build_repository())

    with pytest.raises(ContractQueryError, match="topic_not_found"):
        execute_topic_detail(service, topic_id="unknown-topic", page=1, page_size=20)


def test_topic_detail_reconciles_out_of_range_page_to_last_page() -> None:
    """Reconcile out-of-range topic page requests to the last valid page."""
    service = DatasetDiscoveryService(_build_repository())

    payload = execute_topic_detail(service, topic_id="inflation", page=99, page_size=1).model_dump()

    assert payload["page"] == payload["total_pages"]
    assert payload["items"]
