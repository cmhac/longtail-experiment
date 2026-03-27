"""Contract tests for dataset query entrypoint wrappers and grouping helpers."""

# ruff: noqa: D103, PLR2004

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_catalog_grouping import project_catalog_source_groups
from src.query.dataset_catalog_query import execute_dataset_catalog
from src.query.dataset_detail_query import execute_dataset_detail
from src.query.dataset_discovery_service import DatasetDiscoveryService
from src.query.dataset_recent_updates_query import execute_recent_updates
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
    )
    return DatasetDiscoveryService(repository)


def test_entrypoints_return_validated_models() -> None:
    service = _service()

    search = execute_dataset_search(service, query_text="unemployment", page=1, page_size=20)
    recent = execute_recent_updates(service, limit=5)
    catalog = execute_dataset_catalog(
        service,
        query_text=None,
        source_id=None,
        category=None,
        sort=None,
        page=1,
        page_size=20,
        group_by_source=True,
    )
    detail = execute_dataset_detail(
        service,
        dataset_id="UNRATE",
        from_date=None,
        to_date=None,
    )
    source_detail = execute_source_detail(service, source_id="fred", page=1, page_size=1)
    topic_detail = execute_topic_detail(service, topic_id="inflation", page=1, page_size=1)
    geography_detail = execute_geography_detail(service, geography_id="us", page=1, page_size=1)

    assert search.total_items >= 1
    assert recent.limit == 5
    assert catalog.items
    assert catalog.aggregations.total_dataset_count >= 1
    assert catalog.groups
    assert detail.dataset_id == "UNRATE"
    assert source_detail.total_items >= 1
    assert source_detail.page_size == 1
    assert topic_detail.total_items >= 1
    assert topic_detail.total_pages >= 1
    assert geography_detail.total_items >= 1
    assert geography_detail.page == 1


def test_catalog_grouping_helper_projects_source_buckets() -> None:
    grouped = project_catalog_source_groups(
        [
            {"dataset_id": "GDP", "source": {"id": "bea", "name": "BEA"}},
            {"dataset_id": "UNRATE", "source": {"id": "fred", "name": "FRED"}},
        ]
    )

    assert grouped[0]["source"]["name"] == "BEA"
    assert grouped[1]["dataset_ids"] == ["UNRATE"]
