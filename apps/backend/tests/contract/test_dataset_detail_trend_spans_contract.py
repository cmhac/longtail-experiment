"""US2 contract tests for dataset detail trend span payload compatibility."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_detail_query import execute_dataset_detail
from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_dataset_detail_includes_trend_spans_when_available() -> None:
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
                    "tooltip": {
                        "headline": "Mild downtrend",
                        "detail": "Unemployment decreased through spring 2025",
                    },
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

    assert len(response["trend_spans"]) == 1


def test_dataset_detail_no_trend_baseline_remains_compatible() -> None:
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

    assert response["trend_spans"] == []
