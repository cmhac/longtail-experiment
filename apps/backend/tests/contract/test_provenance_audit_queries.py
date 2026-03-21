"""US2 backend tests for provenance and revision audit retrieval."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src import health_message
from src.contract.errors import ContractQueryError
from src.contract.query.provenance_audit_query import ProvenanceAuditQueryService

EXPECTED_AUDIT_ROWS = 2


class _AuditRepository:
    def fetch_provenance_and_revisions(self, series_key: str) -> list[dict[str, str]]:
        return [
            {
                "series_key": series_key,
                "observation_id": "obs-old",
                "revision_reason": "restatement",
            },
            {
                "series_key": series_key,
                "observation_id": "obs-new",
                "revision_reason": "restatement",
            },
        ]


class _BadAuditRepository:
    def fetch_provenance_and_revisions(self, series_key: str) -> dict[str, str]:
        return {"series_key": series_key}


def test_provenance_audit_query_returns_revision_history() -> None:
    """Audit queries should return both superseded and current observation rows."""
    service = ProvenanceAuditQueryService(repository=_AuditRepository())

    rows = service.fetch_audit_history("CPI.US.ALL")
    assert len(rows) == EXPECTED_AUDIT_ROWS
    assert {row["observation_id"] for row in rows} == {"obs-old", "obs-new"}


def test_provenance_audit_query_enforces_repository_contract() -> None:
    """Audit query service should fail fast for invalid repository adapters."""
    service = ProvenanceAuditQueryService(repository=object())

    with pytest.raises(ContractQueryError):
        service.fetch_audit_history("CPI.US.ALL")


def test_provenance_audit_query_rejects_non_list_response() -> None:
    """Audit query service should reject non-list payloads from repository adapters."""
    service = ProvenanceAuditQueryService(repository=_BadAuditRepository())

    with pytest.raises(ContractQueryError):
        service.fetch_audit_history("CPI.US.ALL")


def test_backend_health_entrypoint_remains_available() -> None:
    """Backend package health helper should stay functional."""
    assert health_message() == "backend-ok"
