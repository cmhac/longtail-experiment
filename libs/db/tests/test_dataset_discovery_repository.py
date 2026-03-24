"""Unit tests for dataset discovery in-memory repository behavior."""

from __future__ import annotations

from datetime import date
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from db.repositories.dataset_discovery_repository import (
    InMemoryDatasetDiscoveryRepository,
)


def _repository() -> InMemoryDatasetDiscoveryRepository:
    return InMemoryDatasetDiscoveryRepository(
        datasets=[
            {
                "dataset_id": "d1",
                "title": "Federal Funds Rate",
                "description": "US policy interest rate",
                "geographic_scope": "United States",
                "topic_tags": ["interest rates", "monetary policy"],
                "source": {"id": "fred", "name": "FRED"},
            },
            {
                "dataset_id": "d2",
                "title": "Gasoline Prices",
                "description": "Weekly gas retail prices",
                "geographic_scope": "United States",
                "topic_tags": ["energy"],
                "source": {"id": "fred", "name": "FRED"},
            },
            {
                "dataset_id": "d3",
                "title": "Manufacturing Output",
                "description": "Factory output index",
                "geographic_scope": "United States",
                "topic_tags": "industry",
                "source": {"id": "bea", "name": "BEA"},
            },
        ],
        observations=[
            {
                "dataset_id": "d1",
                "observed_on": "2026-01-01",
                "reported_at": "2026-01-02T00:00:00Z",
            },
            {
                "dataset_id": "d1",
                "observed_on": "2026-01-03",
                "reported_at": "2026-01-04T00:00:00Z",
            },
            {
                "dataset_id": "d2",
                "observed_on": "2026-01-05",
                "reported_at": "2026-01-06T00:00:00Z",
            },
            {
                "dataset_id": "",
                "observed_on": "2026-01-01",
                "reported_at": "2026-01-01T00:00:00Z",
            },
        ],
    )


def test_search_datasets_matches_metadata_and_tags() -> None:
    repo = _repository()

    rows, total = repo.search_datasets(query_text="interest", page=1, page_size=10)

    assert total == 1
    assert [row["dataset_id"] for row in rows] == ["d1"]
    assert rows[0]["latest_update_at"] == "2026-01-04T00:00:00Z"


def test_search_datasets_paginates_and_sorts_by_latest_update() -> None:
    repo = _repository()

    rows, total = repo.search_datasets(query_text=None, page=1, page_size=2)

    assert total == 3
    assert [row["dataset_id"] for row in rows] == ["d2", "d1"]


def test_list_recent_datasets_applies_limit() -> None:
    repo = _repository()

    rows = repo.list_recent_datasets(limit=1)

    assert len(rows) == 1
    assert rows[0]["dataset_id"] == "d2"


def test_list_catalog_datasets_filters_source_and_orders_rows() -> None:
    repo = _repository()

    rows, total = repo.list_catalog_datasets(
        query_text="united",
        source_id="fred",
        page=1,
        page_size=10,
    )

    assert total == 2
    assert [row["dataset_id"] for row in rows] == ["d1", "d2"]


def test_get_dataset_detail_returns_copy_and_none_for_missing() -> None:
    repo = _repository()

    detail = repo.get_dataset_detail(dataset_id="d1")
    missing = repo.get_dataset_detail(dataset_id="missing")

    assert detail is not None
    assert detail["dataset_id"] == "d1"
    assert missing is None


def test_list_dataset_observations_filters_date_range_and_normalizes_dates() -> None:
    repo = InMemoryDatasetDiscoveryRepository(
        datasets=[{"dataset_id": "d1"}],
        observations=[
            {
                "dataset_id": "d1",
                "observed_on": date(2026, 1, 1),
                "reported_at": "2026-01-01T00:00:00Z",
            },
            {
                "dataset_id": "d1",
                "observed_on": "2026-01-02",
                "reported_at": "2026-01-03T00:00:00Z",
            },
            {
                "dataset_id": "d1",
                "observed_on": "2026-01-03",
                "reported_at": "2026-01-04T00:00:00Z",
            },
            {
                "dataset_id": "d2",
                "observed_on": "2026-01-01",
                "reported_at": "2026-01-01T00:00:00Z",
            },
        ],
    )

    rows = repo.list_dataset_observations(
        dataset_id="d1",
        from_date=date(2026, 1, 2),
        to_date=date(2026, 1, 3),
    )

    assert [row["observed_on"] for row in rows] == ["2026-01-02", "2026-01-03"]


def test_group_catalog_by_source_handles_missing_source_payload() -> None:
    repo = _repository()

    groups = repo.group_catalog_by_source(
        [
            {"dataset_id": "d1", "source": {"id": "fred", "name": "FRED"}},
            {"dataset_id": "d2", "source": {"id": "fred", "name": "FRED"}},
            {"dataset_id": "d3", "source": "invalid-source"},
        ]
    )

    assert groups[0]["source"] == {"id": "", "name": ""}
    assert groups[0]["dataset_ids"] == ["d3"]
    assert groups[1]["source"] == {"id": "fred", "name": "FRED"}
    assert groups[1]["dataset_count"] == 2
