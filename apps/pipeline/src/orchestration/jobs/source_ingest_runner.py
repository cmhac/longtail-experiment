"""Reusable ingest runner with validation and quarantine mapping."""

from __future__ import annotations

from typing import Any

from src.contract.errors import ContractValidationError

from .trend_errors import TrendProcessingError
from .workflow_request import SourceWorkflowRequest
from .workflow_result import SourceWorkflowResult


def quarantine_reason(error: Exception) -> str:
    """Map validation exceptions into deterministic quarantine reason codes."""
    if isinstance(error, ContractValidationError):
        return "contract_validation_failed"
    return "ingest_processing_failed"


class SourceIngestRunner:
    """Execute source records through canonical validation and persistence."""

    def __init__(
        self,
        canonical_ingest_service: Any,
        *,
        trend_runtime_processor: Any | None = None,
    ) -> None:
        """Initialize runner with canonical ingest service dependency."""
        self._canonical_ingest_service = canonical_ingest_service
        self._trend_runtime_processor = trend_runtime_processor

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
        *,
        fallback_series_keys: list[str] | None = None,
    ) -> SourceWorkflowResult:
        """Ingest source records and emit workflow-level counters."""
        accepted_count = 0
        quarantined_count = 0
        failed_count = 0
        accepted_series_keys: set[str] = set()

        for payload in records:
            try:
                self._canonical_ingest_service.ingest_payload(payload)
                accepted_count += 1
                series_key = payload.get("series_key")
                if isinstance(series_key, str) and series_key.strip() != "":
                    accepted_series_keys.add(series_key)
            except Exception as exc:  # pragma: no cover - explicit boundary for runner behavior
                reason_code = quarantine_reason(exc)
                if reason_code == "contract_validation_failed":
                    quarantined_count += 1
                else:
                    failed_count += 1

        series_keys_to_process = set(accepted_series_keys)
        if fallback_series_keys is not None:
            series_keys_to_process.update(
                key.strip() for key in fallback_series_keys if key.strip() != ""
            )

        if self._trend_runtime_processor is not None:
            for series_key in sorted(series_keys_to_process):
                try:
                    self._trend_runtime_processor.process_series(series_key=series_key)
                except Exception as exc:  # pragma: no cover
                    raise TrendProcessingError(
                        f"trend processing failed for series={series_key}: {exc}"
                    ) from exc

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
