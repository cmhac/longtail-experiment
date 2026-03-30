"""FR-010 tests for backend full filter-matrix contract behavior."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.query.canonical_query import CanonicalObservationQueryService
from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository

_FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "filter_matrix_scenarios.json"


class _FilterMatrixRepo:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = rows

    def list_observations(self) -> list[dict[str, object]]:
        return list(self._rows)


def test_filter_matrix_scenarios_match_expected_series() -> None:
    """All fixture scenarios should resolve to the expected series keys."""
    payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    service = CanonicalObservationQueryService(repository=_FilterMatrixRepo(payload["rows"]))

    for scenario in payload["scenarios"]:
        rows = service.fetch_by_filters(
            source_types=set(scenario.get("source_types", [])) or None,
            series_keys=set(scenario.get("series_keys", [])) or None,
            category_ids=set(scenario.get("category_ids", [])) or None,
            geography_ids=set(scenario.get("geography_ids", [])) or None,
        )
        assert {str(row["series_key"]) for row in rows} == set(scenario["expected_series"])


def test_catalog_filter_matrix_applies_source_category_and_sort_consistently() -> None:
    """Catalog source/category/sort combinations should produce aligned filtered rows."""
    datasets, observations = build_discovery_rows()
    service = DatasetDiscoveryService(
        InMemoryDatasetDiscoveryRepository(datasets=datasets, observations=observations)
    )

    filtered = service.list_catalog(
        query_text=None,
        options={
            "source_id": "fred",
            "category": "prices",
            "sort": "title_desc",
            "page": 1,
            "page_size": 20,
        },
        group_by_source=False,
    )

    assert filtered["items"]
    assert all(item["source"]["id"] == "fred" for item in filtered["items"])
    assert all("prices" in item["topic_tags"] for item in filtered["items"])
    assert filtered["sort"] == "title_desc,dataset_id_desc"


def test_catalog_filter_matrix_treats_all_sentinels_as_unset() -> None:
    """Sentinel filter values should resolve to the same scope as unset filters."""
    datasets, observations = build_discovery_rows()
    service = DatasetDiscoveryService(
        InMemoryDatasetDiscoveryRepository(datasets=datasets, observations=observations)
    )

    filtered = service.list_catalog(
        query_text=None,
        options={
            "source_id": "all",
            "category": " all ",
            "sort": "recency",
            "page": 1,
            "page_size": 20,
        },
        group_by_source=False,
    )

    assert filtered["total_items"] == len(datasets)
