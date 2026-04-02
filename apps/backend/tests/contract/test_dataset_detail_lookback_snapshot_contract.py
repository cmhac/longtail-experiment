"""US2 contract tests for lookback snapshot payloads in dataset detail."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_detail_query import execute_dataset_detail
from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_dataset_detail_includes_lookback_snapshot_rows_with_applicability_states() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
        lookback_snapshots_by_dataset={
            "UNRATE": [
                {
                    "lookback_points": 10,
                    "applicability_state": "applicable",
                    "outcome_state": "significant_trend",
                    "trend_label": "mild_sustained_downtrend",
                    "direction": "down",
                    "strength": "mild",
                    "reason_code": None,
                },
                {
                    "lookback_points": 500,
                    "applicability_state": "inapplicable",
                    "outcome_state": None,
                    "trend_label": None,
                    "direction": None,
                    "strength": None,
                    "reason_code": "insufficient_history",
                },
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

    assert response["lookback_trend_snapshots"] == [
        {
            "lookback_points": 10,
            "applicability_state": "applicable",
            "outcome_state": "significant_trend",
            "trend_label": "mild_sustained_downtrend",
            "direction": "down",
            "strength": "mild",
            "reason_code": None,
        },
        {
            "lookback_points": 500,
            "applicability_state": "inapplicable",
            "outcome_state": None,
            "trend_label": None,
            "direction": None,
            "strength": None,
            "reason_code": "insufficient_history",
        },
    ]


def test_dataset_detail_returns_empty_lookback_snapshot_list_when_absent() -> None:
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

    assert response["lookback_trend_snapshots"] == []


def test_dataset_detail_allows_applicable_no_significant_trend_snapshot_shape() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
        lookback_snapshots_by_dataset={
            "UNRATE": [
                {
                    "lookback_points": 2,
                    "applicability_state": "applicable",
                    "outcome_state": "no_significant_trend",
                    "trend_label": None,
                    "direction": None,
                    "strength": None,
                    "reason_code": "applicable",
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

    assert response["lookback_trend_snapshots"] == [
        {
            "lookback_points": 2,
            "applicability_state": "applicable",
            "outcome_state": "no_significant_trend",
            "trend_label": None,
            "direction": None,
            "strength": None,
            "reason_code": "applicable",
        }
    ]
