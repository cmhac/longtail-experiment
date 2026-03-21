"""Backend observability integration checks for contract query paths."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.query.canonical_query import CanonicalObservationQueryService
from src.contract.query.provenance_audit_query import ProvenanceAuditQueryService


class _CanonicalRepo:
    def list_observations(self) -> list[dict[str, object]]:
        return [
            {
                "series_key": "CPI.US.ALL",
                "source_type": "external",
                "trace_id": "trace-123",
                "span_id": "span-abc",
            }
        ]


class _AuditRepo:
    def fetch_provenance_and_revisions(self, series_key: str) -> list[dict[str, str]]:
        return [
            {
                "series_key": series_key,
                "observation_id": "obs-1",
                "trace_id": "trace-123",
            }
        ]


def test_backend_canonical_query_preserves_trace_fields() -> None:
    """Canonical query reads should not strip trace correlation fields."""
    service = CanonicalObservationQueryService(repository=_CanonicalRepo())

    rows = service.fetch_by_series_key("CPI.US.ALL")

    assert rows[0]["trace_id"] == "trace-123"
    assert rows[0]["span_id"] == "span-abc"


def test_backend_audit_query_preserves_trace_fields() -> None:
    """Audit query reads should preserve trace identifiers for investigations."""
    service = ProvenanceAuditQueryService(repository=_AuditRepo())

    rows = service.fetch_audit_history("CPI.US.ALL")

    assert rows[0]["trace_id"] == "trace-123"
