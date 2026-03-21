"""US2 tests for provenance immutability guarantees."""

from __future__ import annotations

import sys
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src import health_message
from src.contract.observability.logging import get_contract_logger
from src.contract.observability.tracing import get_contract_tracer
from src.contract.schemas.canonical_observation import CanonicalObservation
from src.contract.schemas.provenance_record import ProvenanceRecord


def test_provenance_record_is_immutable_after_creation() -> None:
    """Persisted provenance records must not allow field mutation."""
    record = ProvenanceRecord(
        observation_id="obs-001",
        source_release_id="release-2026-03",
        source_document_ref="https://example.org/release/2026-03",
        source_published_at=datetime(2026, 3, 1, tzinfo=UTC),
        source_retrieval_at=datetime(2026, 3, 2, tzinfo=UTC),
        ingest_run_id="run-123",
        acquisition_method="api",
        immutable_flag=True,
    )

    with pytest.raises((ValidationError, TypeError, AttributeError)):
        record.source_document_ref = "https://example.org/changed"


def test_provenance_record_requires_source_document_reference() -> None:
    """Accepted provenance must include a source document reference."""
    with pytest.raises(ValidationError):
        ProvenanceRecord(
            observation_id="obs-001",
            source_release_id="release-2026-03",
            source_document_ref="",
            source_published_at=datetime(2026, 3, 1, tzinfo=UTC),
            source_retrieval_at=datetime(2026, 3, 2, tzinfo=UTC),
            ingest_run_id="run-123",
            acquisition_method="api",
            immutable_flag=True,
        )


def test_pipeline_helpers_and_canonical_schema_are_usable() -> None:
    """US2 tests also assert shared helper and schema modules stay healthy."""
    assert health_message() == "pipeline-ok"
    assert get_contract_logger() is not None
    assert get_contract_tracer() is not None

    payload = CanonicalObservation(
        source_name="BLS",
        source_type="external",
        series_key="CPI.US.ALL",
        metric_name="Consumer Price Index",
        frequency_granularity="monthly",
        observed_on=date(2026, 3, 1),
        reported_at=datetime(2026, 3, 2, tzinfo=UTC),
        value=Decimal("303.1000"),
    )
    assert payload.series_key == "CPI.US.ALL"
