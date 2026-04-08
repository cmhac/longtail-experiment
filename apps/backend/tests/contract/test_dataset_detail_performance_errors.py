"""Contract tests for dataset detail error invariants."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.errors import ContractQueryError
from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_dataset_detail_not_found_invariance_contract() -> None:
    datasets, observations = build_discovery_rows()
    service = DatasetDiscoveryService(
        InMemoryDatasetDiscoveryRepository(datasets=datasets, observations=observations)
    )

    with pytest.raises(ContractQueryError, match="dataset_not_found"):
        service.get_dataset_detail(dataset_id="NOPE", from_date=None, to_date=None)


def test_dataset_detail_invalid_date_range_invariance_contract() -> None:
    datasets, observations = build_discovery_rows()
    service = DatasetDiscoveryService(
        InMemoryDatasetDiscoveryRepository(datasets=datasets, observations=observations)
    )

    with pytest.raises(ContractQueryError, match="from_date must be on or before to_date"):
        service.get_dataset_detail(
            dataset_id="UNRATE",
            from_date="2025-02-01",
            to_date="2025-01-01",
        )
