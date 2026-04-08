"""US2 contract coverage for observation-level as-of descriptor shape."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_detail_query import execute_dataset_detail
from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.contract.fixtures.dataset_detail_asof_trend_fixtures import (
    build_observation_asof_available_descriptor,
)
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_dataset_detail_includes_observation_asof_descriptor_fields_per_observation() -> None:
    lookback_points = 25
    datasets, observations = build_discovery_rows()
    seeded_observations = [dict(observation) for observation in observations]
    seeded_observations[0]["as_of_trend_descriptor"] = build_observation_asof_available_descriptor(
        observed_on="2026-01-01",
        selected_lookback_points=50,
    )
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=seeded_observations,
        canonical_trends_by_dataset={
            "UNRATE": {
                "descriptor_version": "v2",
                "descriptor_state": "available",
                "trend_label": "mild_sustained_downtrend",
                "direction": "down",
                "confidence_score": 0.73,
                "selected_lookback_points": lookback_points,
                "observed_on": "2026-02-01",
                "dominant_measure_family": "theil_sen",
                "reason_code": None,
            }
        },
        lookback_snapshots_by_dataset={
            "UNRATE": [
                {
                    "lookback_points": lookback_points,
                    "applicability_state": "applicable",
                    "descriptor_state": "available",
                    "trend_label": "mild_sustained_downtrend",
                    "direction": "down",
                    "confidence_score": 0.73,
                    "dominant_measure_family": "theil_sen",
                    "theil_sen_slope": -0.1,
                    "theil_sen_low_slope": -0.2,
                    "theil_sen_high_slope": -0.05,
                    "kendall_tau": -0.41,
                    "kendall_p_value": 0.01,
                    "preprocessing": {
                        "smoothing_method": "none",
                        "smoothing_parameters": {},
                        "seasonal_adjustment_method": "none",
                        "seasonal_periods": [],
                        "seasonal_reliability_state": "not_applicable",
                        "preprocess_version": "v2",
                    },
                    "ols_diagnostics": {
                        "slope": -0.09,
                        "intercept": 4.7,
                        "r_squared": 0.55,
                        "p_value": 0.02,
                    },
                    "reason_code": None,
                }
            ]
        },
    )
    service = DatasetDiscoveryService(repository)

    response = execute_dataset_detail(
        service,
        dataset_id="UNRATE",
        from_date=None,
        to_date=None,
    ).model_dump()

    asof_keys = {
        "descriptor_version",
        "descriptor_state",
        "trend_label",
        "direction",
        "confidence_score",
        "dominant_measure_family",
        "selected_lookback_points",
        "observed_on",
        "reason_code",
    }
    assert all("as_of_trend_descriptor" in observation for observation in response["observations"])
    assert all(
        set(observation["as_of_trend_descriptor"].keys()) == asof_keys
        for observation in response["observations"]
    )
    assert response["observations"][0]["as_of_trend_descriptor"]["descriptor_state"] == "available"
    assert (
        response["observations"][1]["as_of_trend_descriptor"]["descriptor_state"] == "unavailable"
    )
    assert response["canonical_trend_descriptor"]["descriptor_state"] == "available"
    assert response["lookback_trend_evidence"][0]["lookback_points"] == lookback_points
