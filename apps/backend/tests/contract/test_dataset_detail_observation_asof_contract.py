"""Phase 2 foundational contract tests for observation-level as-of descriptors."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.errors import ContractQueryError
from src.query.dataset_detail_query import execute_dataset_detail
from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.contract.fixtures.dataset_detail_asof_trend_fixtures import (
    build_observation_asof_available_descriptor,
)
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_dataset_detail_observations_default_unavailable_asof_descriptor_when_missing() -> None:
    datasets, observations = build_discovery_rows()
    seeded_observations = [dict(observation) for observation in observations]
    seeded_observations[0]["as_of_trend_descriptor"] = build_observation_asof_available_descriptor(
        observed_on=str(seeded_observations[0]["observed_on"])
    )
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=seeded_observations,
    )
    service = DatasetDiscoveryService(repository)

    response = execute_dataset_detail(
        service,
        dataset_id="UNRATE",
        from_date=None,
        to_date=None,
    ).model_dump()

    assert all("as_of_trend_descriptor" in observation for observation in response["observations"])
    assert response["observations"][0]["as_of_trend_descriptor"]["descriptor_state"] == "available"
    assert response["observations"][1]["as_of_trend_descriptor"] == {
        "descriptor_state": "unavailable",
        "trend_label": None,
        "direction": None,
        "strength": None,
        "selected_lookback_points": None,
        "observed_on": None,
        "reason_code": "missing_observation_asof_descriptor",
    }


def test_dataset_detail_invalid_observation_asof_payload_raises_contract_error() -> None:
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
