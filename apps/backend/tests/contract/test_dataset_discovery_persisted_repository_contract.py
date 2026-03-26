"""Contract coverage for persisted discovery repository behavior."""

# ruff: noqa: D103, E501, UP017

from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy import Engine

from src.query.dataset_discovery_persisted_repository import PersistedDatasetDiscoveryRepository


class _FakeResult:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def mappings(self) -> _FakeResult:
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows


class _FakeConnection:
    def __init__(
        self,
        *,
        dataset_rows: list[dict[str, Any]],
        observation_rows: list[dict[str, Any]],
    ) -> None:
        self._dataset_rows = dataset_rows
        self._observation_rows = observation_rows

    def execute(self, statement: object, parameters: dict[str, Any] | None = None) -> _FakeResult:
        sql = str(statement)
        if "FROM data_series ds" in sql and "MAX(o.reported_at)" in sql:
            return _FakeResult(self._dataset_rows)
        if "FROM observations o" in sql:
            params = parameters or {}
            dataset_id = str(params.get("dataset_id", ""))
            from_date = params.get("from_date")
            to_date = params.get("to_date")

            filtered: list[dict[str, Any]] = []
            for row in self._observation_rows:
                if str(row.get("dataset_id", "")) != dataset_id:
                    continue
                observed_on = row["observed_on"]
                if from_date is not None and observed_on < from_date:
                    continue
                if to_date is not None and observed_on > to_date:
                    continue
                filtered.append(row)
            filtered.sort(key=lambda row: (row["observed_on"], row["reported_at"]))
            return _FakeResult(filtered)

        raise AssertionError(f"Unexpected SQL executed: {sql}")

    def __enter__(self) -> _FakeConnection:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        del exc_type, exc, tb


class _FakeEngine:
    def __init__(
        self, *, dataset_rows: list[dict[str, Any]], observation_rows: list[dict[str, Any]]
    ) -> None:
        self._dataset_rows = dataset_rows
        self._observation_rows = observation_rows

    def connect(self) -> _FakeConnection:
        return _FakeConnection(
            dataset_rows=self._dataset_rows,
            observation_rows=self._observation_rows,
        )


def _build_repository() -> PersistedDatasetDiscoveryRepository:
    dataset_rows = [
        {
            "dataset_id": "INT.US.FEDFUNDS",
            "source_name": "Federal Reserve",
            "source_type": "external",
            "metric_name": "effective_rate",
            "title": "Effective Federal Funds Rate",
            "description": "Policy rate",
            "geographic_scope": "US",
            "topic_tags": ["interest rates", "monetary policy"],
            "latest_update_at": datetime(2026, 3, 6, tzinfo=timezone.utc),
        },
        {
            "dataset_id": "LABOR.US.UNRATE",
            "source_name": "BLS",
            "source_type": "external",
            "metric_name": "unemployment_rate",
            "title": "Unemployment Rate",
            "description": None,
            "geographic_scope": None,
            "topic_tags": [],
            "latest_update_at": datetime(2026, 2, 10, tzinfo=timezone.utc),
        },
    ]
    observation_rows = [
        {
            "dataset_id": "INT.US.FEDFUNDS",
            "observed_on": date(2026, 1, 1),
            "value": 4.33,
            "reported_at": datetime(2026, 2, 3, tzinfo=timezone.utc),
            "attributes": None,
        },
        {
            "dataset_id": "INT.US.FEDFUNDS",
            "observed_on": date(2026, 1, 2),
            "value": 4.35,
            "reported_at": datetime(2026, 2, 4, tzinfo=timezone.utc),
            "attributes": {"revision": 1},
        },
    ]
    engine = _FakeEngine(dataset_rows=dataset_rows, observation_rows=observation_rows)
    return PersistedDatasetDiscoveryRepository(engine=cast(Engine, engine))


def test_search_and_recent_are_persisted_and_sorted() -> None:
    repository = _build_repository()

    rows, total_items = repository.search_datasets(query_text="policy", page=1, page_size=10)
    recent = repository.list_recent_datasets(limit=1)

    assert total_items == 1
    assert rows[0]["dataset_id"] == "INT.US.FEDFUNDS"
    assert rows[0]["source"] == {"id": "federal-reserve", "name": "Federal Reserve"}
    metadata = cast(dict[str, Any], rows[0]["metadata"])
    assert metadata["source_type"] == "external"
    assert recent[0]["dataset_id"] == "INT.US.FEDFUNDS"


def test_catalog_detail_and_grouping_support_source_filtering() -> None:
    repository = _build_repository()

    catalog_rows, total_items = repository.list_catalog_datasets(
        query_text=None,
        options={
            "source_id": "federal-reserve",
            "category": None,
            "sort": "recency",
            "page": 1,
            "page_size": 10,
        },
    )
    groups = repository.group_catalog_by_source(catalog_rows)
    detail = repository.get_dataset_detail(dataset_id="INT.US.FEDFUNDS")
    missing = repository.get_dataset_detail(dataset_id="UNKNOWN")

    assert total_items == 1
    assert catalog_rows[0]["dataset_id"] == "INT.US.FEDFUNDS"
    assert groups == [
        {
            "source": {"id": "federal-reserve", "name": "Federal Reserve"},
            "dataset_count": 1,
            "dataset_ids": ["INT.US.FEDFUNDS"],
        }
    ]
    assert detail is not None
    assert detail["dataset_id"] == "INT.US.FEDFUNDS"
    assert missing is None


def test_source_list_and_detail_use_persisted_source_projection() -> None:
    repository = _build_repository()

    sources = repository.list_sources()
    source_detail = repository.get_source_detail(source_id="federal-reserve")
    missing_source_detail = repository.get_source_detail(source_id="unknown")

    assert sources == [
        {
            "id": "bls",
            "name": "BLS",
            "dataset_count": 1,
            "source_type": "external",
        },
        {
            "id": "federal-reserve",
            "name": "Federal Reserve",
            "dataset_count": 1,
            "source_type": "external",
        },
    ]
    assert source_detail is not None
    assert source_detail["source"] == {
        "id": "federal-reserve",
        "name": "Federal Reserve",
        "dataset_count": 1,
        "source_type": "external",
    }
    assert [
        item["dataset_id"] for item in cast(list[dict[str, Any]], source_detail["datasets"])
    ] == ["INT.US.FEDFUNDS"]
    assert missing_source_detail is None


def test_topic_and_geography_detail_use_persisted_metadata_projection() -> None:
    repository = _build_repository()

    topic_detail = repository.get_topic_detail(topic_id="interest-rates")
    missing_topic_detail = repository.get_topic_detail(topic_id="unknown-topic")
    geography_detail = repository.get_geography_detail(geography_id="us")
    missing_geography_detail = repository.get_geography_detail(geography_id="unknown-geo")

    assert topic_detail is not None
    assert topic_detail["topic"] == {
        "id": "interest-rates",
        "label": "interest rates",
        "dataset_count": 1,
    }
    assert [
        item["dataset_id"] for item in cast(list[dict[str, Any]], topic_detail["datasets"])
    ] == ["INT.US.FEDFUNDS"]
    assert missing_topic_detail is None

    assert geography_detail is not None
    assert geography_detail["geography"] == {
        "id": "us",
        "label": "US",
        "dataset_count": 1,
    }
    assert [
        item["dataset_id"] for item in cast(list[dict[str, Any]], geography_detail["datasets"])
    ] == ["INT.US.FEDFUNDS"]
    assert missing_geography_detail is None


def test_observations_apply_date_filters_and_shape() -> None:
    repository = _build_repository()

    rows = repository.list_dataset_observations(
        dataset_id="INT.US.FEDFUNDS",
        from_date=date(2026, 1, 2),
        to_date=date(2026, 1, 2),
    )

    assert rows == [
        {
            "observed_on": "2026-01-02",
            "value": 4.35,
            "reported_at": "2026-02-04T00:00:00+00:00",
            "attributes": {"revision": 1},
        }
    ]


def test_search_matches_dataset_id_and_source_name_tokens() -> None:
    repository = _build_repository()

    dataset_id_rows, dataset_id_total = repository.search_datasets(
        query_text="FEDFUNDS",
        page=1,
        page_size=10,
    )
    source_rows, source_total = repository.search_datasets(
        query_text="federal reserve",
        page=1,
        page_size=10,
    )

    assert dataset_id_total == 1
    assert dataset_id_rows[0]["dataset_id"] == "INT.US.FEDFUNDS"
    assert source_total == 1
    assert source_rows[0]["dataset_id"] == "INT.US.FEDFUNDS"
