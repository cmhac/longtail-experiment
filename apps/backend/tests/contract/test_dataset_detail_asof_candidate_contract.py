"""Contract tests for as-of descriptor candidate correctness."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_asof_candidate_mapping_prefers_latest_valid_candidate() -> None:
    datasets, observations = build_discovery_rows()
    seeded = [dict(row) for row in observations if str(row.get("dataset_id", "")) == "UNRATE"]
    seeded[0]["as_of_trend_candidates"] = [
        {
            "descriptor_version": "v2",
            "descriptor_state": "available",
            "trend_label": "mild_sustained_downtrend",
            "direction": "down",
            "confidence_score": 0.64,
            "selected_lookback_points": 25,
            "observed_on": seeded[0]["observed_on"],
            "dominant_measure_family": "theil_sen",
            "reason_code": None,
            "_candidate_reported_at": seeded[0]["reported_at"],
            "_candidate_created_at": "2026-02-11T00:00:00+00:00",
        }
    ]

    service = DatasetDiscoveryService(
        InMemoryDatasetDiscoveryRepository(datasets=datasets, observations=seeded)
    )

    payload = service.get_dataset_detail(dataset_id="UNRATE", from_date=None, to_date=None)

    assert (
        payload["observations"][0]["as_of_trend_descriptor"]["trend_label"]
        == "mild_sustained_downtrend"
    )
