"""US1 backend canonical observation read tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src import health_message
from src.contract.errors import ContractQueryError
from src.contract.query.canonical_query import CanonicalObservationQueryService

EXPECTED_ROWS = 2


class _ObservationRepo:
    def __init__(self) -> None:
        self._rows: list[dict[str, object]] = []

    def upsert_value(self, series_key: str, observed_on: str, value: str) -> None:
        self._rows.append(
            {
                "series_key": series_key,
                "observed_on": observed_on,
                "value": value,
            }
        )

    def list_observations(self) -> list[dict[str, object]]:
        return list(self._rows)


def test_backend_query_reads_canonical_rows_by_series_key() -> None:
    """Query service should return only canonical rows for the requested series."""
    repo = _ObservationRepo()
    repo.upsert_value("CPI.US.ALL", "2026-01-01", "302.5")
    repo.upsert_value("CPI.US.ALL", "2026-02-01", "303.2")
    repo.upsert_value("TEMP.US.NYC", "2026-02-01", "4.1")

    service = CanonicalObservationQueryService(repository=repo)
    rows = service.fetch_by_series_key("CPI.US.ALL")

    assert len(rows) == EXPECTED_ROWS
    assert all(row["series_key"] == "CPI.US.ALL" for row in rows)


def test_backend_query_errors_when_repository_contract_missing() -> None:
    """Service should raise a contract query error when repository shape is invalid."""
    service = CanonicalObservationQueryService(repository=object())

    with pytest.raises(ContractQueryError):
        service.fetch_by_series_key("CPI.US.ALL")


def test_backend_entrypoint_health_message() -> None:
    """Backend package entrypoint should return its static health message."""
    assert health_message() == "backend-ok"
