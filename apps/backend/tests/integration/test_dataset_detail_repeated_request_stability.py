"""Integration tests for repeated dataset detail request stability."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.contract.fixtures.dataset_detail_performance_fixtures import (
    measure_call_durations_ms,
    median_duration_ms,
)
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository

_MAX_LATENCY_TARGET_MS = 1000
_MEDIAN_LATENCY_TARGET_MS = 300


def test_repeated_detail_requests_remain_stable() -> None:
    datasets, observations = build_discovery_rows()
    service = DatasetDiscoveryService(
        InMemoryDatasetDiscoveryRepository(datasets=datasets, observations=observations)
    )

    samples = measure_call_durations_ms(
        lambda: service.get_dataset_detail(dataset_id="UNRATE", from_date=None, to_date=None),
        repetitions=30,
    )

    assert max(samples) < _MAX_LATENCY_TARGET_MS
    assert median_duration_ms(samples) < _MEDIAN_LATENCY_TARGET_MS
