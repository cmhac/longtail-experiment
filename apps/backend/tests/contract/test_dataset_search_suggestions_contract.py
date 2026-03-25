"""Contract tests for likely-match dataset suggestions behavior."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from src.query.dataset_search_suggestions_query import execute_dataset_search_suggestions
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_suggestions_respect_limit_and_include_required_fields() -> None:
    datasets, observations = build_discovery_rows()
    service = DatasetDiscoveryService(
        InMemoryDatasetDiscoveryRepository(datasets=datasets, observations=observations)
    )

    response = execute_dataset_search_suggestions(service, query_text="rate", limit=1).model_dump()

    assert response["limit"] == 1
    assert len(response["items"]) <= 1
    if response["items"]:
        item = response["items"][0]
        assert item["dataset_id"]
        assert item["title"]
        assert "source" in item


def test_suggestions_are_ranked_descending_then_stable() -> None:
    datasets, observations = build_discovery_rows()
    service = DatasetDiscoveryService(
        InMemoryDatasetDiscoveryRepository(datasets=datasets, observations=observations)
    )

    response = execute_dataset_search_suggestions(service, query_text="rate", limit=5).model_dump()

    ranks = [float(item["rank_score"]) for item in response["items"]]
    assert ranks == sorted(ranks, reverse=True)


def test_suggestions_return_empty_items_for_no_matches() -> None:
    datasets, observations = build_discovery_rows()
    service = DatasetDiscoveryService(
        InMemoryDatasetDiscoveryRepository(datasets=datasets, observations=observations)
    )

    response = execute_dataset_search_suggestions(
        service,
        query_text="zzzzzzzz",
        limit=5,
    ).model_dump()

    assert response["query"] == "zzzzzzzz"
    assert response["items"] == []
