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
        trend_event_rows: list[dict[str, Any]],
        canonical_descriptor_rows: list[dict[str, Any]],
    ) -> None:
        self._dataset_rows = dataset_rows
        self._observation_rows = observation_rows
        self._trend_event_rows = trend_event_rows
        self._canonical_descriptor_rows = canonical_descriptor_rows

    def execute(  # noqa: PLR0911, PLR0912
        self,
        statement: object,
        parameters: dict[str, Any] | None = None,
    ) -> _FakeResult:
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

        if "FROM trend_records tr" in sql:
            if "LIMIT :limit" in sql:
                params = parameters or {}
                limit = int(params.get("limit", 0))
                rows = sorted(
                    self._trend_event_rows,
                    key=lambda row: (
                        row["start_period"],
                        row["dataset_id"],
                    ),
                    reverse=True,
                )
                return _FakeResult(rows[:limit])

            if "WHERE ds.series_key = :dataset_id" in sql:
                params = parameters or {}
                dataset_id = str(params.get("dataset_id", ""))
                rows = [
                    row
                    for row in self._trend_event_rows
                    if str(row.get("dataset_id", "")) == dataset_id
                ]
                rows.sort(key=lambda row: (row["start_period"], row["created_at"]))
                return _FakeResult(rows)
        if "FROM trend_canonical_descriptors tcd" in sql:
            if "ROW_NUMBER() OVER" in sql:
                rows = [
                    {
                        "dataset_id": row["dataset_id"],
                        "descriptor_state": row["descriptor_state"],
                        "trend_label": row["trend_label"],
                        "direction": row["direction"],
                        "strength": row["strength"],
                        "selected_lookback_points": row["selected_lookback_points"],
                        "observed_on": row["observed_on"],
                        "reason_code": row["reason_code"],
                    }
                    for row in self._canonical_descriptor_rows
                ]
                return _FakeResult(rows)
            params = parameters or {}
            dataset_id = str(params.get("dataset_id", ""))
            rows = [
                row
                for row in self._canonical_descriptor_rows
                if str(row.get("dataset_id", "")) == dataset_id
            ]
            rows.sort(
                key=lambda row: (
                    row["observed_on"],
                    row["created_at"],
                ),
                reverse=True,
            )
            return _FakeResult(rows[:1])
        if "FROM trend_lookback_evaluations tle" in sql:
            params = parameters or {}
            dataset_id = str(params.get("dataset_id", ""))
            rows: list[dict[str, Any]] = []
            if dataset_id == "INT.US.FEDFUNDS":
                rows = [
                    {
                        "lookback_points": 10,
                        "applicability_state": "applicable",
                        "outcome_state": "significant_trend",
                        "trend_label": "mild_sustained_downtrend",
                        "direction": "down",
                        "strength": "mild",
                        "reason_code": None,
                    },
                    {
                        "lookback_points": 500,
                        "applicability_state": "inapplicable",
                        "outcome_state": None,
                        "trend_label": None,
                        "direction": None,
                        "strength": None,
                        "reason_code": "insufficient_history",
                    },
                ]
            return _FakeResult(rows)

        raise AssertionError(f"Unexpected SQL executed: {sql}")

    def __enter__(self) -> _FakeConnection:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        del exc_type, exc, tb


class _FakeEngine:
    def __init__(
        self,
        *,
        dataset_rows: list[dict[str, Any]],
        observation_rows: list[dict[str, Any]],
        trend_event_rows: list[dict[str, Any]],
        canonical_descriptor_rows: list[dict[str, Any]],
    ) -> None:
        self._dataset_rows = dataset_rows
        self._observation_rows = observation_rows
        self._trend_event_rows = trend_event_rows
        self._canonical_descriptor_rows = canonical_descriptor_rows

    def connect(self) -> _FakeConnection:
        return _FakeConnection(
            dataset_rows=self._dataset_rows,
            observation_rows=self._observation_rows,
            trend_event_rows=self._trend_event_rows,
            canonical_descriptor_rows=self._canonical_descriptor_rows,
        )


def _build_repository() -> PersistedDatasetDiscoveryRepository:
    dataset_rows = [
        {
            "dataset_id": "INT.US.FEDFUNDS",
            "source_key": "fred",
            "source_name": "Federal Reserve",
            "source_title": "Federal Reserve Economic Data",
            "source_description": "Economic time series published by the St. Louis Fed.",
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
            "source_key": "bls",
            "source_name": "BLS",
            "source_title": "Bureau of Labor Statistics",
            "source_description": "US labor market and price statistics.",
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
    trend_event_rows = [
        {
            "dataset_id": "INT.US.FEDFUNDS",
            "source_key": "fred",
            "source_title": "Federal Reserve Economic Data",
            "title": "Effective Federal Funds Rate",
            "direction": "down",
            "strength": "mild",
            "trend_label": "mild_sustained_downtrend",
            "seasonality_classification": "none",
            "start_period": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "end_period": datetime(2026, 2, 1, tzinfo=timezone.utc),
            "is_ongoing": False,
            "created_at": datetime(2026, 1, 2, tzinfo=timezone.utc),
        },
        {
            "dataset_id": "LABOR.US.UNRATE",
            "source_key": "bls",
            "source_title": "Bureau of Labor Statistics",
            "title": "Unemployment Rate",
            "direction": "up",
            "strength": "strong",
            "trend_label": "strong_sustained_uptrend",
            "seasonality_classification": "none",
            "start_period": datetime(2026, 2, 1, tzinfo=timezone.utc),
            "end_period": None,
            "is_ongoing": True,
            "created_at": datetime(2026, 2, 2, tzinfo=timezone.utc),
        },
    ]
    canonical_descriptor_rows = [
        {
            "dataset_id": "INT.US.FEDFUNDS",
            "descriptor_state": "available",
            "trend_label": "mild_sustained_downtrend",
            "direction": "down",
            "strength": "mild",
            "selected_lookback_points": 25,
            "observed_on": date(2026, 2, 1),
            "reason_code": None,
            "created_at": datetime(2026, 1, 2, tzinfo=timezone.utc),
        },
        {
            "dataset_id": "LABOR.US.UNRATE",
            "descriptor_state": "available",
            "trend_label": "strong_sustained_uptrend",
            "direction": "up",
            "strength": "strong",
            "selected_lookback_points": 10,
            "observed_on": date(2026, 2, 1),
            "reason_code": None,
            "created_at": datetime(2026, 2, 2, tzinfo=timezone.utc),
        },
    ]
    engine = _FakeEngine(
        dataset_rows=dataset_rows,
        observation_rows=observation_rows,
        trend_event_rows=trend_event_rows,
        canonical_descriptor_rows=canonical_descriptor_rows,
    )
    return PersistedDatasetDiscoveryRepository(engine=cast(Engine, engine))


def test_search_and_recent_are_persisted_and_sorted() -> None:
    repository = _build_repository()

    rows, total_items = repository.search_datasets(query_text="policy", page=1, page_size=10)
    recent = repository.list_recent_datasets(limit=1)

    assert total_items == 1
    assert rows[0]["dataset_id"] == "INT.US.FEDFUNDS"
    assert rows[0]["source"] == {
        "id": "fred",
        "name": "Federal Reserve Economic Data",
    }
    metadata = cast(dict[str, Any], rows[0]["metadata"])
    assert metadata["source_type"] == "external"
    assert rows[0]["canonical_trend_descriptor"] == {
        "descriptor_state": "available",
        "trend_label": "mild_sustained_downtrend",
        "direction": "down",
        "strength": "mild",
        "selected_lookback_points": 25,
        "observed_on": "2026-02-01",
        "reason_code": None,
    }
    assert recent[0]["dataset_id"] == "INT.US.FEDFUNDS"
    assert recent[0]["canonical_trend_descriptor"] == {
        "descriptor_state": "available",
        "trend_label": "mild_sustained_downtrend",
        "direction": "down",
        "strength": "mild",
        "selected_lookback_points": 25,
        "observed_on": "2026-02-01",
        "reason_code": None,
    }


def test_catalog_detail_and_grouping_support_source_filtering() -> None:
    repository = _build_repository()

    catalog_rows, total_items = repository.list_catalog_datasets(
        query_text=None,
        options={
            "source_id": "fred",
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
    assert catalog_rows[0]["canonical_trend_descriptor"] == {
        "descriptor_state": "available",
        "trend_label": "mild_sustained_downtrend",
        "direction": "down",
        "strength": "mild",
        "selected_lookback_points": 25,
        "observed_on": "2026-02-01",
        "reason_code": None,
    }
    assert groups == [
        {
            "source": {"id": "fred", "name": "Federal Reserve Economic Data"},
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
    source_detail = repository.get_source_detail(source_id="fred", page=1, page_size=1)
    missing_source_detail = repository.get_source_detail(source_id="unknown", page=1, page_size=1)

    assert sources == [
        {
            "id": "bls",
            "title": "Bureau of Labor Statistics",
            "description": "US labor market and price statistics.",
            "dataset_count": 1,
            "source_type": "external",
        },
        {
            "id": "fred",
            "title": "Federal Reserve Economic Data",
            "description": "Economic time series published by the St. Louis Fed.",
            "dataset_count": 1,
            "source_type": "external",
        },
    ]
    assert source_detail is not None
    assert source_detail["source"] == {
        "id": "fred",
        "title": "Federal Reserve Economic Data",
        "description": "Economic time series published by the St. Louis Fed.",
        "dataset_count": 1,
        "source_type": "external",
    }
    assert [item["dataset_id"] for item in cast(list[dict[str, Any]], source_detail["items"])] == [
        "INT.US.FEDFUNDS"
    ]
    source_item = cast(list[dict[str, Any]], source_detail["items"])[0]
    assert source_item["canonical_trend_descriptor"] == {
        "descriptor_state": "available",
        "trend_label": "mild_sustained_downtrend",
        "direction": "down",
        "strength": "mild",
        "selected_lookback_points": 25,
        "observed_on": "2026-02-01",
        "reason_code": None,
    }
    assert source_detail["total_items"] == 1
    assert missing_source_detail is None


def test_topic_and_geography_detail_use_persisted_metadata_projection() -> None:
    repository = _build_repository()

    topic_detail = repository.get_topic_detail(topic_id="interest-rates", page=1, page_size=1)
    missing_topic_detail = repository.get_topic_detail(
        topic_id="unknown-topic", page=1, page_size=1
    )
    geography_detail = repository.get_geography_detail(geography_id="us", page=1, page_size=1)
    missing_geography_detail = repository.get_geography_detail(
        geography_id="unknown-geo", page=1, page_size=1
    )

    assert topic_detail is not None
    assert topic_detail["topic"] == {
        "id": "interest-rates",
        "label": "interest rates",
        "dataset_count": 1,
    }
    assert [item["dataset_id"] for item in cast(list[dict[str, Any]], topic_detail["items"])] == [
        "INT.US.FEDFUNDS"
    ]
    topic_item = cast(list[dict[str, Any]], topic_detail["items"])[0]
    assert topic_item["canonical_trend_descriptor"] == {
        "descriptor_state": "available",
        "trend_label": "mild_sustained_downtrend",
        "direction": "down",
        "strength": "mild",
        "selected_lookback_points": 25,
        "observed_on": "2026-02-01",
        "reason_code": None,
    }
    assert topic_detail["total_items"] == 1
    assert missing_topic_detail is None

    assert geography_detail is not None
    assert geography_detail["geography"] == {
        "id": "us",
        "label": "US",
        "dataset_count": 1,
    }
    assert [
        item["dataset_id"] for item in cast(list[dict[str, Any]], geography_detail["items"])
    ] == ["INT.US.FEDFUNDS"]
    geography_item = cast(list[dict[str, Any]], geography_detail["items"])[0]
    assert geography_item["canonical_trend_descriptor"] == {
        "descriptor_state": "available",
        "trend_label": "mild_sustained_downtrend",
        "direction": "down",
        "strength": "mild",
        "selected_lookback_points": 25,
        "observed_on": "2026-02-01",
        "reason_code": None,
    }
    assert geography_detail["total_items"] == 1
    assert missing_geography_detail is None


def test_source_topic_and_geography_detail_pagination_is_stable() -> None:
    repository = _build_repository()

    source_detail = repository.get_source_detail(source_id="fred", page=2, page_size=1)
    topic_detail = repository.get_topic_detail(topic_id="interest-rates", page=2, page_size=1)
    geography_detail = repository.get_geography_detail(geography_id="us", page=2, page_size=1)

    assert source_detail is not None
    assert source_detail["items"] == []
    assert source_detail["total_items"] == 1

    assert topic_detail is not None
    assert topic_detail["items"] == []
    assert topic_detail["total_items"] == 1

    assert geography_detail is not None
    assert geography_detail["items"] == []
    assert geography_detail["total_items"] == 1


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


def test_recent_trend_events_projection_uses_persisted_rows() -> None:
    repository = _build_repository()

    trend_events = repository.list_recent_trend_events(limit=1)

    assert trend_events == [
        {
            "dataset_id": "LABOR.US.UNRATE",
            "source": {
                "id": "bls",
                "name": "Bureau of Labor Statistics",
            },
            "title": "Unemployment Rate",
            "direction": "up",
            "strength": "strong",
            "start_period": "2026-02-01",
        }
    ]


def test_dataset_canonical_descriptor_projection_uses_latest_descriptor_row() -> None:
    repository = _build_repository()

    descriptor = repository.get_latest_dataset_canonical_trend_descriptor(
        dataset_id="INT.US.FEDFUNDS"
    )

    assert descriptor == {
        "descriptor_state": "available",
        "trend_label": "mild_sustained_downtrend",
        "direction": "down",
        "strength": "mild",
        "selected_lookback_points": 25,
        "observed_on": "2026-02-01",
        "reason_code": None,
    }
