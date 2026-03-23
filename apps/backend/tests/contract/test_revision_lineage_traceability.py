"""US3 sampled lineage traceability test for audit outputs."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.query.provenance_audit_query import ProvenanceAuditQueryService


class _TraceabilityRepo:
    def fetch_provenance_and_revisions(self, series_key: str) -> list[dict[str, object]]:
        return [
            {
                "series_key": series_key,
                "superseded_observation_id": "obs-old",
                "current_observation_id": "obs-new",
                "revision_reason": "restatement",
            }
        ]


def test_revision_lineage_rows_remain_queryable() -> None:
    """Confirms sampled lineage fields remain queryable in audit history output."""
    service = ProvenanceAuditQueryService(repository=_TraceabilityRepo())

    rows = service.fetch_audit_history("CPI.US.ALL")

    assert rows[0]["superseded_observation_id"] == "obs-old"
    assert rows[0]["current_observation_id"] == "obs-new"
