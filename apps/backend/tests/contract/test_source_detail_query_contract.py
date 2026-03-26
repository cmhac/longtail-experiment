"""Contract tests for source detail query behavior."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.errors import ContractQueryError
from src.query.dataset_discovery_service import DatasetDiscoveryService
from src.query.source_detail_query import execute_source_detail
from tests.fixtures.source_discovery_repository import build_source_discovery_repository

EXPECTED_DATASET_COUNT = 2


def test_source_detail_returns_source_context_and_only_matching_datasets() -> None:
    """Return one source plus only datasets attributed to that source."""
    service = DatasetDiscoveryService(build_source_discovery_repository())

    payload = execute_source_detail(service, source_id="fred").model_dump()

    assert payload["source"]["id"] == "fred"
    assert payload["source"]["dataset_count"] == EXPECTED_DATASET_COUNT
    assert [item["dataset_id"] for item in payload["datasets"]] == ["CPIAUCSL", "UNRATE"]
    assert all(item["source"]["id"] == "fred" for item in payload["datasets"])


def test_source_detail_raises_not_found_for_unknown_source() -> None:
    """Raise the not-found contract error for unknown source ids."""
    service = DatasetDiscoveryService(build_source_discovery_repository())

    with pytest.raises(ContractQueryError, match="source_not_found"):
        execute_source_detail(service, source_id="unknown")
