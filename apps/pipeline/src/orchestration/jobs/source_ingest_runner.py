"""Reusable ingest runner with validation and quarantine mapping."""

from __future__ import annotations

from typing import Any

from src.contract.errors import ContractValidationError

from .workflow_request import SourceWorkflowRequest
from .workflow_result import SourceWorkflowResult


def quarantine_reason(error: Exception) -> str:
    """Map validation exceptions into deterministic quarantine reason codes."""
    if isinstance(error, ContractValidationError):
        return "contract_validation_failed"
    return "ingest_processing_failed"


class SourceIngestRunner:
    """Execute source records through canonical validation and persistence."""

    def __init__(self, canonical_ingest_service: Any) -> None:
        """Initialize runner with canonical ingest service dependency."""
        self._canonical_ingest_service = canonical_ingest_service

    def sync_source_metadata(
        self,
        *,
        source_key: str,
        source_name: str,
        source_title: str,
        source_description: str,
        source_type: str,
    ) -> None:
        """Persist source metadata when supported by the backing service."""
        if hasattr(self._canonical_ingest_service, "sync_source_metadata"):
            self._canonical_ingest_service.sync_source_metadata(
                source_key=source_key,
                source_name=source_name,
                source_title=source_title,
                source_description=source_description,
                source_type=source_type,
            )

    def run_records(
        self,
        request: SourceWorkflowRequest,
        records: list[dict[str, object]],
    ) -> SourceWorkflowResult:
        """Ingest source records and emit workflow-level counters."""
        accepted_count = 0
        quarantined_count = 0
        failed_count = 0

        for payload in records:
            try:
                self._canonical_ingest_service.ingest_payload(payload)
                accepted_count += 1
            except Exception as exc:  # pragma: no cover - explicit boundary for runner behavior
                reason_code = quarantine_reason(exc)
                if reason_code == "contract_validation_failed":
                    quarantined_count += 1
                else:
                    failed_count += 1

        if failed_count > 0 and accepted_count == 0:
            status = "failure"
        elif quarantined_count > 0 or failed_count > 0:
            status = "partial_success"
        else:
            status = "success"

        return SourceWorkflowResult(
            source_key=request.source_key,
            status=status,
            accepted_count=accepted_count,
            quarantined_count=quarantined_count,
            failed_count=failed_count,
        )
