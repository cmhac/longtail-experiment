"""Contract tests for dataset-detail scope scaling behavior."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_persisted_repository import PersistedDatasetDiscoveryRepository

_MAX_EXPECTED_QUERY_COUNT = 3


class _FakeResult:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def mappings(self) -> _FakeResult:
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows

    def one_or_none(self) -> dict[str, Any] | None:
        return self._rows[0] if self._rows else None


class _FakeConnection:
    def __init__(self) -> None:
        self.query_count = 0

    def execute(
        self, statement: object, parameters: dict[str, object] | None = None
    ) -> _FakeResult:
        del parameters
        self.query_count += 1
        sql = str(statement)
        if "WHERE ds.series_key = :dataset_id" in sql and "FROM data_series ds" in sql:
            return _FakeResult(
                [
                    {
                        "dataset_id": "UNRATE",
                        "source_key": "fred",
                        "source_name": "FRED",
                        "source_title": "Federal Reserve Economic Data",
                        "source_description": "desc",
                        "source_type": "federal",
                        "metric_name": "Unemployment Rate",
                        "title": "Unemployment Rate",
                        "description": "desc",
                        "geographic_scope": "United States",
                        "topic_tags": ["labor"],
                        "latest_update_at": datetime.fromisoformat("2026-04-01T00:00:00+00:00"),
                    }
                ]
            )
        if "FROM trend_canonical_descriptors tcd" in sql:
            return _FakeResult([])
        if "recent_observation_window" in sql and "has_recent_notification" in sql:
            return _FakeResult([{"has_recent_notification": False}])
        raise AssertionError(f"Unexpected SQL executed: {sql}")

    def __enter__(self) -> _FakeConnection:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        del exc_type, exc, tb


class _FakeEngine:
    def __init__(self) -> None:
        self.connection = _FakeConnection()

    def connect(self) -> _FakeConnection:
        return self.connection


def test_detail_metadata_query_does_not_scan_full_catalog() -> None:
    engine = _FakeEngine()
    repository = PersistedDatasetDiscoveryRepository(engine=engine)  # type: ignore[arg-type]

    repository.get_dataset_detail(dataset_id="UNRATE")

    assert engine.connection.query_count <= _MAX_EXPECTED_QUERY_COUNT
