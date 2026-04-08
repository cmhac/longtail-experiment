"""US2 contract tests for malformed canonical trend payload handling."""

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


def test_dataset_detail_invalid_canonical_payload_raises_contract_error() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
        canonical_trends_by_dataset={
            "UNRATE": {
                "descriptor_version": "v2",
                "descriptor_state": "available",
                "trend_label": "mild_sustained_downtrend",
                "direction": "down",
                "confidence_score": 0.81,
                "selected_lookback_points": 25,
                "observed_on": "2026-01-01",
                "dominant_measure_family": "invalid-family",
                "reason_code": None,
            }
        },
    )
    service = DatasetDiscoveryService(repository)

    with pytest.raises(
        ContractQueryError,
        match="dataset_detail_canonical_payload_invalid",
    ):
        execute_dataset_detail(
            service,
            dataset_id="UNRATE",
            from_date=None,
            to_date=None,
        )


def test_dataset_detail_invalid_lookback_evidence_payload_raises_contract_error() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
        lookback_snapshots_by_dataset={
            "UNRATE": [{"lookback_points": "invalid", "applicability_state": "applicable"}]
        },
    )
    service = DatasetDiscoveryService(repository)

    with pytest.raises(
        ContractQueryError, match="dataset_detail_lookback_evidence_payload_invalid"
    ):
        execute_dataset_detail(
            service,
            dataset_id="UNRATE",
            from_date=None,
            to_date=None,
        )
