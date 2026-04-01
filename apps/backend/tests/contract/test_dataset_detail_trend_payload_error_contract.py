"""US2 contract test for malformed dataset detail trend payload handling."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.errors import ContractQueryError
from src.query.dataset_detail_query import execute_dataset_detail
from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_dataset_detail_malformed_trend_payload_raises_contract_error() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
        trend_spans_by_dataset={
            "UNRATE": [
                {
                    "start_period": "2025-01-01",
                    "end_period": "2025-04-01",
                    "direction": "down",
                    "trend_label": "mild_sustained_downtrend",
                }
            ]
        },
    )
    service = DatasetDiscoveryService(repository)

    with pytest.raises(ContractQueryError, match="dataset_detail_trend_payload_invalid"):
        execute_dataset_detail(
            service,
            dataset_id="UNRATE",
            from_date=None,
            to_date=None,
        )
