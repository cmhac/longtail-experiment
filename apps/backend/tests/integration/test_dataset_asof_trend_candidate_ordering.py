"""US1 integration tests for repository-level observation as-of candidate ordering."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_persisted_repository import PersistedDatasetDiscoveryRepository


class _FakeResult:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def mappings(self) -> _FakeResult:
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows


class _FakeConnection:
    def execute(
        self,
        statement: object,
        parameters: dict[str, object] | None = None,
    ) -> _FakeResult:
        del parameters
        sql = str(statement)
        if "SELECT o.id, o.observed_on, o.value, o.reported_at, o.attributes" in sql:
            return _FakeResult(
                [
                    {
                        "id": 100,
                        "observed_on": "2026-02-01",
                        "value": 4.1,
                        "reported_at": "2026-02-10T00:00:00Z",
                        "attributes": {"revision": 0},
                    },
                    {
                        "id": 101,
                        "observed_on": "2026-02-01",
                        "value": 4.2,
                        "reported_at": "2026-02-20T00:00:00Z",
                        "attributes": {"revision": 1},
                    },
                ]
            )

        if "SELECT" in sql and "FROM trend_canonical_descriptors tcd" in sql:
            return _FakeResult(
                [
                    {
                        "observation_id": 101,
                        "candidate_observed_on": "2026-02-01",
                        "candidate_reported_at": "2026-02-20T00:00:00Z",
                        "candidate_created_at": "2026-02-21T00:00:00Z",
                        "descriptor_version": "v2",
                        "descriptor_state": "available",
                        "trend_label": "strong_accelerating_downtrend",
                        "direction": "down",
                        "confidence_score": 0.91,
                        "selected_lookback_points": 50,
                        "dominant_measure_family": "theil_sen",
                        "reason_code": None,
                    },
                    {
                        "observation_id": 100,
                        "candidate_observed_on": "2026-02-01",
                        "candidate_reported_at": "2026-02-10T00:00:00Z",
                        "candidate_created_at": "2026-02-11T00:00:00Z",
                        "descriptor_version": "v2",
                        "descriptor_state": "available",
                        "trend_label": "mild_sustained_downtrend",
                        "direction": "down",
                        "confidence_score": 0.64,
                        "selected_lookback_points": 25,
                        "dominant_measure_family": "theil_sen",
                        "reason_code": None,
                    },
                    {
                        "observation_id": 101,
                        "candidate_observed_on": "2026-02-01",
                        "candidate_reported_at": "2026-02-10T00:00:00Z",
                        "candidate_created_at": "2026-02-11T00:00:00Z",
                        "descriptor_version": "v2",
                        "descriptor_state": "available",
                        "trend_label": "mild_sustained_downtrend",
                        "direction": "down",
                        "confidence_score": 0.64,
                        "selected_lookback_points": 25,
                        "dominant_measure_family": "theil_sen",
                        "reason_code": None,
                    },
                ]
            )

        raise AssertionError(f"Unexpected SQL executed: {sql}")

    def __enter__(self) -> _FakeConnection:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        del exc_type, exc, tb


class _FakeEngine:
    def connect(self) -> _FakeConnection:
        return _FakeConnection()


def test_repository_orders_observation_candidates() -> None:
    """Repository should keep deterministic report-time candidate ordering."""
    repository = PersistedDatasetDiscoveryRepository(engine=_FakeEngine())  # type: ignore[arg-type]

    payload = repository.list_dataset_observations(
        dataset_id="UNRATE",
        from_date=None,
        to_date=None,
    )

    first_candidates = cast(list[dict[str, Any]], payload[0]["as_of_trend_candidates"])
    second_candidates = cast(list[dict[str, Any]], payload[1]["as_of_trend_candidates"])

    assert [candidate["trend_label"] for candidate in first_candidates] == [
        "mild_sustained_downtrend"
    ]
    assert [candidate["trend_label"] for candidate in second_candidates] == [
        "strong_accelerating_downtrend",
        "mild_sustained_downtrend",
    ]
