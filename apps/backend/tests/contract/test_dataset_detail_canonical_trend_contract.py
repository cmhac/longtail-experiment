"""US2 contract tests for dataset detail canonical trend descriptor payload."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_detail_query import execute_dataset_detail
from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_dataset_detail_includes_available_canonical_descriptor_when_present() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
        canonical_trends_by_dataset={
            "UNRATE": {
                "descriptor_state": "available",
                "trend_label": "mild_sustained_downtrend",
                "direction": "down",
                "strength": "mild",
                "selected_lookback_points": 25,
                "observed_on": "2026-03-01",
                "reason_code": None,
            }
        },
    )
    service = DatasetDiscoveryService(repository)

    response = execute_dataset_detail(
        service,
        dataset_id="UNRATE",
        from_date=None,
        to_date=None,
    ).model_dump()

    assert response["canonical_trend_descriptor"] == {
        "descriptor_state": "available",
        "descriptor_version": "v2",
        "trend_label": "mild_sustained_downtrend",
        "direction": "down",
        "strength": "mild",
        "dominant_measure_family": "none",
        "confidence_score": None,
        "selected_lookback_points": 25,
        "observed_on": "2026-03-01",
        "reason_code": None,
    }
    assert isinstance(response["has_recent_notification"], bool)


def test_dataset_detail_defaults_to_unavailable_canonical_descriptor_when_missing() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = execute_dataset_detail(
        service,
        dataset_id="UNRATE",
        from_date=None,
        to_date=None,
    ).model_dump()

    assert response["canonical_trend_descriptor"] == {
        "descriptor_state": "unavailable",
        "descriptor_version": "v2",
        "trend_label": None,
        "direction": None,
        "strength": None,
        "dominant_measure_family": "none",
        "confidence_score": None,
        "selected_lookback_points": None,
        "observed_on": None,
        "reason_code": "missing_canonical_descriptor",
    }
    assert isinstance(response["has_recent_notification"], bool)
