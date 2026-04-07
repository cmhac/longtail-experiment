"""US1 contract tests for mixed availability observation-level as-of resolution."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_detail_query import execute_dataset_detail
from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_dataset_detail_supports_mixed_available_and_unavailable_asof_states() -> None:
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
        }
    ]
    seeded_observations[1]["as_of_trend_candidates"] = []

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

    assert response["observations"][0]["as_of_trend_descriptor"]["descriptor_state"] == "available"
    assert response["observations"][1]["as_of_trend_descriptor"] == {
        "descriptor_version": "v2",
        "descriptor_state": "unavailable",
        "trend_label": None,
        "direction": None,
        "strength": None,
        "confidence_score": None,
        "dominant_measure_family": "none",
        "selected_lookback_points": None,
        "observed_on": None,
        "reason_code": "missing_observation_asof_descriptor",
    }


def test_dataset_detail_sets_report_time_reason_when_candidates_after_report_time() -> None:
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
            "_candidate_reported_at": "2026-01-11T00:00:00Z",
            "_candidate_created_at": "2026-01-12T00:00:00Z",
        }
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
        "descriptor_version": "v2",
        "descriptor_state": "unavailable",
        "trend_label": None,
        "direction": None,
        "strength": None,
        "confidence_score": None,
        "dominant_measure_family": "none",
        "selected_lookback_points": None,
        "observed_on": None,
        "reason_code": "observation_reported_before_candidate",
    }
