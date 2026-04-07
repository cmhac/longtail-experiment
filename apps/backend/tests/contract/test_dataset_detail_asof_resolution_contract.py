"""US1 contract tests for deterministic observation-level as-of resolution."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_detail_query import execute_dataset_detail
from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_dataset_detail_prefers_latest_created_candidate_for_same_observation_context() -> None:
    datasets, observations = build_discovery_rows()
    seeded_observations = [dict(observation) for observation in observations]
    seeded_observations[0]["as_of_trend_candidates"] = [
        {
            "descriptor_state": "available",
            "trend_label": "mild_sustained_downtrend",
            "direction": "down",
            "strength": "mild",
            "selected_lookback_points": 25,
            "observed_on": "2026-01-01",
            "reason_code": None,
            "_candidate_reported_at": "2026-01-10T00:00:00Z",
            "_candidate_created_at": "2026-01-12T00:00:00Z",
        },
        {
            "descriptor_state": "available",
            "trend_label": "strong_accelerating_downtrend",
            "direction": "down",
            "strength": "strong",
            "selected_lookback_points": 50,
            "observed_on": "2026-01-01",
            "reason_code": None,
            "_candidate_reported_at": "2026-01-10T00:00:00Z",
            "_candidate_created_at": "2026-01-12T01:00:00Z",
        },
    ]
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

    assert response["observations"][0]["as_of_trend_descriptor"] == {
        "descriptor_state": "available",
        "descriptor_version": "v2",
        "trend_label": "strong_accelerating_downtrend",
        "direction": "down",
        "strength": "strong",
        "dominant_measure_family": "none",
        "confidence_score": None,
        "selected_lookback_points": 50,
        "observed_on": "2026-01-01",
        "reason_code": None,
    }


def test_dataset_detail_asof_resolution_is_deterministic_for_repeated_requests() -> None:
    datasets, observations = build_discovery_rows()
    seeded_observations = [dict(observation) for observation in observations]
    seeded_observations[0]["as_of_trend_candidates"] = [
        {
            "descriptor_state": "available",
            "trend_label": "mild_sustained_downtrend",
            "direction": "down",
            "strength": "mild",
            "selected_lookback_points": 25,
            "observed_on": "2026-01-01",
            "reason_code": None,
            "_candidate_reported_at": "2026-01-10T00:00:00Z",
            "_candidate_created_at": "2026-01-12T00:00:00Z",
        },
        {
            "descriptor_state": "available",
            "trend_label": "strong_accelerating_downtrend",
            "direction": "down",
            "strength": "strong",
            "selected_lookback_points": 50,
            "observed_on": "2026-01-01",
            "reason_code": None,
            "_candidate_reported_at": "2026-01-10T00:00:00Z",
            "_candidate_created_at": "2026-01-12T01:00:00Z",
        },
    ]
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=seeded_observations,
    )
    service = DatasetDiscoveryService(repository)

    first_payload = execute_dataset_detail(
        service,
        dataset_id="UNRATE",
        from_date=None,
        to_date=None,
    ).model_dump()
    second_payload = execute_dataset_detail(
        service,
        dataset_id="UNRATE",
        from_date=None,
        to_date=None,
    ).model_dump()

    assert (
        first_payload["observations"][0]["as_of_trend_descriptor"]
        == second_payload["observations"][0]["as_of_trend_descriptor"]
    )
