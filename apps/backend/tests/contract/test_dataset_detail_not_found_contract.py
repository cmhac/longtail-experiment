"""US3 contract tests for explicit dataset-not-found behavior."""

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


def test_detail_unknown_dataset_raises_not_found_contract_error() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    with pytest.raises(ContractQueryError, match="dataset_not_found"):
        service.get_dataset_detail(
            dataset_id="UNKNOWN",
            from_date=None,
            to_date=None,
        )
