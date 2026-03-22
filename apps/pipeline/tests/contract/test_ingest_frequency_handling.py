"""US1 mixed-frequency ingest integration tests."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Protocol

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src import health_message
from src.contract.errors import ContractValidationError
from src.contract.observability.logging import get_contract_logger
from src.contract.observability.tracing import get_contract_tracer
from src.contract.services.canonical_ingest_service import CanonicalIngestService

EXPECTED_ROWS = 2


class _Observation(Protocol):
    series_key: object
    frequency_granularity: object


class _ObservationRepo:
    def __init__(self) -> None:
        self._rows: list[dict[str, object]] = []

    def upsert_observation(self, observation: _Observation) -> None:
        row: dict[str, object] = {
            "series_key": str(observation.series_key),
            "frequency_granularity": str(observation.frequency_granularity),
        }
        self._rows.append(row)

    def list_observations(self) -> list[dict[str, object]]:
        return list(self._rows)


class _DualModeObservationRepo:
    """Repository exposing both write methods to assert upsert_observation precedence."""

    def __init__(self) -> None:
        self.observation_calls = 0
        self.value_calls = 0

    def upsert_observation(self, observation: _Observation) -> None:
        self.observation_calls += 1

    def upsert_value(self, _series_key: object, _observed_on: object, _value: object) -> None:
        self.value_calls += 1


def test_mixed_frequency_payloads_are_ingested_to_canonical_store() -> None:
    """Daily and monthly payloads should persist as canonical rows."""
    repo = _ObservationRepo()
    service = CanonicalIngestService(repository=repo)

    service.ingest_payload(
        {
            "source_name": "BLS",
            "source_type": "external",
            "series_key": "CPI.US.ALL",
            "metric_name": "Consumer Price Index",
            "frequency": "monthly",
            "date": "2026-01-01",
            "reported_at": "2026-02-01T00:00:00Z",
            "value": "302.5",
        }
    )
    service.ingest_payload(
        {
            "source_name": "NOAA",
            "source_type": "external",
            "series_key": "TEMP.US.NYC",
            "metric_name": "Average Temperature",
            "frequency": "daily",
            "date": "2026-01-02",
            "reported_at": "2026-01-02T12:00:00Z",
            "value": "4.3",
        }
    )

    rows = repo.list_observations()
    assert len(rows) == EXPECTED_ROWS
    assert {row["frequency_granularity"] for row in rows} == {"monthly", "daily"}


def test_pipeline_entrypoint_and_observability_helpers_are_wired() -> None:
    """Pipeline entrypoint and observability utilities should be callable."""
    assert health_message() == "pipeline-ok"
    assert get_contract_logger() is not None
    assert get_contract_tracer() is not None


def test_invalid_payload_raises_contract_validation_error() -> None:
    """Invalid payloads should be converted to a contract validation error."""
    repo = _ObservationRepo()
    service = CanonicalIngestService(repository=repo)

    with pytest.raises(ContractValidationError):
        service.ingest_payload(
            {
                "source_type": "external",
                "series_key": "MISSING.SOURCE.NAME",
                "metric_name": "Invalid Sample",
                "frequency": "daily",
                "date": "2026-01-02",
                "reported_at": "2026-01-02T12:00:00Z",
                "value": "4.3",
            }
        )


def test_canonical_ingest_prefers_upsert_observation_when_available() -> None:
    """Canonical service should use upsert_observation when repository supports both APIs."""
    repo = _DualModeObservationRepo()
    service = CanonicalIngestService(repository=repo)

    service.ingest_payload(
        {
            "source_name": "FRED",
            "source_type": "external",
            "series_key": "INT.US.FEDFUNDS",
            "metric_name": "Effective Federal Funds Rate",
            "frequency": "daily",
            "date": "2026-01-02",
            "reported_at": "2026-01-02T12:00:00Z",
            "value": "4.3",
        }
    )

    assert repo.observation_calls == 1
    assert repo.value_calls == 0
