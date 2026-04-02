"""US2 contract failures for malformed observation as-of descriptor payloads."""

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


def test_dataset_detail_malformed_observation_asof_payload_raises_contract_error() -> None:
    datasets, observations = build_discovery_rows()
    seeded_observations = [dict(observation) for observation in observations]
    seeded_observations[0]["as_of_trend_descriptor"] = {
        "descriptor_state": "available",
        "trend_label": "mild_sustained_downtrend",
    }
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=seeded_observations,
    )
    service = DatasetDiscoveryService(repository)

    with pytest.raises(
        ContractQueryError,
        match="dataset_detail_observation_asof_payload_invalid:UNRATE:2026-01-01",
    ):
        execute_dataset_detail(
            service,
            dataset_id="UNRATE",
            from_date=None,
            to_date=None,
        )
