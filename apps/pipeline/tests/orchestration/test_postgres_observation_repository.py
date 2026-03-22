"""Integration tests for Postgres observation repository behavior."""

from __future__ import annotations

import sys
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Protocol
from uuid import uuid4

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.resources.postgres_observation_repository import (
    PostgresObservationRepository,
)


class _Observation(Protocol):
    source_name: str
    source_type: str
    series_key: str
    metric_name: str
    frequency_granularity: str
    observed_on: date
    reported_at: datetime
    value: Decimal
    attributes: dict[str, str]


class _CanonicalObservation:
    def __init__(self, *, series_key: str, observed_on: date, value: Decimal) -> None:
        self.source_name = "FRED"
        self.source_type = "external"
        self.series_key = series_key
        self.metric_name = "Effective Federal Funds Rate"
        self.frequency_granularity = "daily"
        self.observed_on = observed_on
        self.reported_at = datetime.now(tz=UTC)
        self.value = value
        self.attributes = {"provider_series_id": "FEDFUNDS"}


def _repo_or_skip() -> PostgresObservationRepository:
    repo = PostgresObservationRepository()
    try:
        repo.read_latest_observed_on(series_key=f"probe-{uuid4()}")
    except Exception as exc:  # pragma: no cover - environment-dependent integration guard
        pytest.skip(f"postgres runtime DB unavailable for observation repository test: {exc}")
    return repo


def test_observation_repository_upserts_and_reads_latest_checkpoint() -> None:
    """Latest checkpoint should track the max observed date for a series."""
    repo = _repo_or_skip()
    series_key = f"INT.US.FEDFUNDS.TEST.{uuid4()}"

    repo.upsert_observation(
        _CanonicalObservation(
            series_key=series_key,
            observed_on=date(2026, 1, 1),
            value=Decimal("4.10"),
        )
    )
    repo.upsert_observation(
        _CanonicalObservation(
            series_key=series_key,
            observed_on=date(2026, 1, 2),
            value=Decimal("4.11"),
        )
    )

    assert repo.read_latest_observed_on(series_key=series_key) == date(2026, 1, 2)


def test_observation_repository_upsert_is_idempotent_per_series_date() -> None:
    """Repeated writes for the same series/date should update, not duplicate."""
    repo = _repo_or_skip()
    series_key = f"INT.US.FEDFUNDS.TEST.{uuid4()}"
    observed_on = date(2026, 2, 1)

    repo.upsert_observation(
        _CanonicalObservation(series_key=series_key, observed_on=observed_on, value=Decimal("4.20"))
    )
    repo.upsert_observation(
        _CanonicalObservation(series_key=series_key, observed_on=observed_on, value=Decimal("4.25"))
    )

    rows = repo.read_series_observations(series_key=series_key)
    assert len(rows) == 1
    assert Decimal(str(rows[0]["value"])) == Decimal("4.25")
