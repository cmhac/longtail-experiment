"""US2 contract tests for canonical trend descriptors in dataset summary surfaces."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_catalog_query import execute_dataset_catalog
from src.query.dataset_discovery_service import DatasetDiscoveryService
from src.query.dataset_search_query import execute_dataset_search
from src.query.geography_detail_query import execute_geography_detail
from src.query.source_detail_query import execute_source_detail
from src.query.topic_detail_query import execute_topic_detail
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def _service() -> DatasetDiscoveryService:
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
                "confidence_score": 0.83,
                "dominant_measure_family": "theil_sen",
                "selected_lookback_points": 25,
                "observed_on": "2026-03-01",
                "reason_code": None,
            }
        },
    )
    return DatasetDiscoveryService(repository)


def test_search_summary_items_include_canonical_trend_descriptor() -> None:
    service = _service()

    payload = execute_dataset_search(
        service,
        query_text="labor",
        page=1,
        page_size=20,
    ).model_dump()

    assert payload["items"]
    assert payload["items"][0]["canonical_trend_descriptor"] == {
        "descriptor_state": "available",
        "descriptor_version": "v2",
        "trend_label": "mild_sustained_downtrend",
        "direction": "down",
        "dominant_measure_family": "theil_sen",
        "confidence_score": 0.83,
        "selected_lookback_points": 25,
        "observed_on": "2026-03-01",
        "reason_code": None,
    }


def test_catalog_summary_items_include_canonical_trend_descriptor() -> None:
    service = _service()

    payload = execute_dataset_catalog(
        service,
        query_text="labor",
        source_id=None,
        category=None,
        sort="recency",
        page=1,
        page_size=20,
        group_by_source=False,
    ).model_dump()

    assert payload["items"]
    assert payload["items"][0]["canonical_trend_descriptor"] == {
        "descriptor_state": "available",
        "descriptor_version": "v2",
        "trend_label": "mild_sustained_downtrend",
        "direction": "down",
        "dominant_measure_family": "theil_sen",
        "confidence_score": 0.83,
        "selected_lookback_points": 25,
        "observed_on": "2026-03-01",
        "reason_code": None,
    }


def test_source_topic_and_geography_summary_items_include_canonical_trend_descriptor() -> None:
    service = _service()

    source_payload = execute_source_detail(
        service,
        source_id="fred",
        page=1,
        page_size=20,
    ).model_dump()
    topic_payload = execute_topic_detail(
        service,
        topic_id="labor",
        page=1,
        page_size=20,
    ).model_dump()
    geography_payload = execute_geography_detail(
        service,
        geography_id="us",
        page=1,
        page_size=20,
    ).model_dump()

    expected_unrate_descriptor = {
        "descriptor_state": "available",
        "descriptor_version": "v2",
        "trend_label": "mild_sustained_downtrend",
        "direction": "down",
        "dominant_measure_family": "theil_sen",
        "confidence_score": 0.83,
        "selected_lookback_points": 25,
        "observed_on": "2026-03-01",
        "reason_code": None,
    }
    source_items = {item["dataset_id"]: item for item in source_payload["items"]}
    topic_items = {item["dataset_id"]: item for item in topic_payload["items"]}
    geography_items = {item["dataset_id"]: item for item in geography_payload["items"]}

    assert source_items["UNRATE"]["canonical_trend_descriptor"] == expected_unrate_descriptor
    assert topic_items["UNRATE"]["canonical_trend_descriptor"] == expected_unrate_descriptor
    assert geography_items["UNRATE"]["canonical_trend_descriptor"] == expected_unrate_descriptor

    for item in source_payload["items"] + topic_payload["items"] + geography_payload["items"]:
        assert item["canonical_trend_descriptor"]["descriptor_state"] in {
            "available",
            "unavailable",
        }
