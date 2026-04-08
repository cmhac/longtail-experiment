"""US2 contract tests for canonical trend descriptors in recent dataset updates."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from src.query.dataset_recent_updates_query import execute_recent_updates
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_recent_dataset_items_include_canonical_trend_descriptor() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
        canonical_trends_by_dataset={
            "UNRATE": {
                "descriptor_version": "v2",
                "descriptor_state": "available",
                "trend_label": "mild_sustained_downtrend",
                "direction": "down",
                "confidence_score": 0.71,
                "dominant_measure_family": "theil_sen",
                "selected_lookback_points": 25,
                "observed_on": "2026-03-01",
                "reason_code": None,
            }
        },
    )
    service = DatasetDiscoveryService(repository)

    payload = execute_recent_updates(service, limit=5).model_dump()
    dataset_items = [
        item
        for item in payload["items"]
        if item.get("item_type", "dataset_update") == "dataset_update"
    ]

    assert dataset_items
    by_dataset_id = {item["dataset_id"]: item for item in dataset_items}
    assert by_dataset_id["UNRATE"]["canonical_trend_descriptor"] == {
        "descriptor_state": "available",
        "descriptor_version": "v2",
        "trend_label": "mild_sustained_downtrend",
        "direction": "down",
        "dominant_measure_family": "theil_sen",
        "confidence_score": 0.71,
        "selected_lookback_points": 25,
        "observed_on": "2026-03-01",
        "reason_code": None,
    }
    assert isinstance(by_dataset_id["UNRATE"]["has_recent_notification"], bool)


def test_recent_dataset_items_default_canonical_trend_descriptor_when_missing() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    payload = execute_recent_updates(service, limit=5).model_dump()
    dataset_items = [
        item
        for item in payload["items"]
        if item.get("item_type", "dataset_update") == "dataset_update"
    ]

    assert dataset_items
    assert dataset_items[0]["canonical_trend_descriptor"] == {
        "descriptor_state": "unavailable",
        "descriptor_version": "v2",
        "trend_label": None,
        "direction": None,
        "dominant_measure_family": "none",
        "confidence_score": None,
        "selected_lookback_points": None,
        "observed_on": None,
        "reason_code": "missing_canonical_descriptor",
    }
    assert isinstance(dataset_items[0]["has_recent_notification"], bool)
