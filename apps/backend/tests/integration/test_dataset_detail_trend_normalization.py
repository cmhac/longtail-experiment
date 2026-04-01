"""US2 integration test for non-overlapping trend span normalization."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_detail_query import execute_dataset_detail
from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository

EXPECTED_SPAN_COUNT = 2


def test_dataset_detail_normalizes_overlapping_trend_spans() -> None:
    """Overlapping trend spans should be normalized into non-overlapping intervals."""
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
        trend_spans_by_dataset={
            "UNRATE": [
                {
                    "start_period": "2025-01-01",
                    "end_period": "2025-05-01",
                    "direction": "down",
                    "trend_label": "down",
                    "tooltip": {"headline": "Down", "detail": "Long span"},
                },
                {
                    "start_period": "2025-03-01",
                    "end_period": "2025-06-01",
                    "direction": "up",
                    "trend_label": "up",
                    "tooltip": {"headline": "Up", "detail": "Overlap"},
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

    spans = response["trend_spans"]
    assert len(spans) == EXPECTED_SPAN_COUNT
    assert spans[0]["end_period"] <= spans[1]["start_period"]
