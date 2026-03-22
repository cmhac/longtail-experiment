"""US3 integration test for ingest audit query compatibility."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.query.provenance_audit_query import ProvenanceAuditQueryService


class _AuditRepo:
    def fetch_provenance_and_revisions(self, series_key: str) -> list[dict[str, object]]:
        return [
            {
                "series_key": series_key,
                "observation_id": "obs-new",
                "revision_reason": "restatement",
            }
        ]

    def fetch_conflict_ids_for_series(self, series_key: str) -> list[str]:
        return [f"conf-{series_key}-1"]


def test_audit_query_returns_conflict_ids_in_projection() -> None:
    service = ProvenanceAuditQueryService(repository=_AuditRepo())

    rows = service.fetch_audit_history("CPI.US.ALL")

    assert rows[0]["conflict_ids"] == ["conf-CPI.US.ALL-1"]
