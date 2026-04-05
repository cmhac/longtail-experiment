"""Reusable ingest runner with validation and quarantine mapping."""

from __future__ import annotations

from typing import Any, Literal, cast

from src.contract.errors import ContractValidationError

from .trend_errors import TrendProcessingError
from .workflow_request import SourceWorkflowRequest
from .workflow_result import SourceWorkflowResult


def _is_true_irregular_cadence_failure(cadence_decision: object) -> bool:
    if not isinstance(cadence_decision, dict):
        return False
    decision = cast(dict[str, object], cadence_decision)
    return decision.get("cadence_state") == "irregular_rejected" and decision.get(
        "reason_code"
    ) in {
        "mixed_cadence_families",
        "no_supported_cadence_gaps",
        "irregular_gap_ratio_exceeds_threshold",
    }


def quarantine_reason(error: Exception) -> str:
    """Map validation exceptions into deterministic quarantine reason codes."""
    if isinstance(error, ContractValidationError):
        return "contract_validation_failed"
    return "ingest_processing_failed"


def _build_series_keys_to_process(
    *,
    accepted_series_keys: set[str],
    fallback_series_keys: list[str] | None,
) -> list[str]:
    series_keys_to_process = set(accepted_series_keys)
    if fallback_series_keys is not None:
        series_keys_to_process.update(
            key.strip() for key in fallback_series_keys if key.strip() != ""
        )
    return sorted(series_keys_to_process)


def _normalize_cadence_decision(
    *,
    series_key: str,
    cadence_decision: object,
) -> dict[str, object] | None:
    if not isinstance(cadence_decision, dict):
        return None
    decision = cast(dict[str, object], cadence_decision)
    return {
        "series_key": series_key,
        "cadence_state": decision.get("cadence_state"),
        "inferred_cadence": decision.get("inferred_cadence"),
        "irregular_gap_count": decision.get("irregular_gap_count"),
        "total_interval_count": decision.get("total_interval_count"),
        "irregular_gap_ratio": decision.get("irregular_gap_ratio"),
        "reason_code": decision.get("reason_code"),
        "reason_detail": decision.get("reason_detail"),
    }


def _cadence_reason_code(cadence_decision: object) -> str:
    if isinstance(cadence_decision, dict):
        value = cast(dict[str, object], cadence_decision).get("reason_code")
        if isinstance(value, str) and value.strip() != "":
            return value
    return "unknown_reason"


def _derive_status(
    *,
    accepted_count: int,
    quarantined_count: int,
    failed_count: int,
) -> Literal["success", "partial_success", "failure"]:
    if failed_count > 0 and accepted_count == 0:
        return "failure"
    if quarantined_count > 0 or failed_count > 0:
        return "partial_success"
    return "success"


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

        series_keys_to_process = _build_series_keys_to_process(
            accepted_series_keys=accepted_series_keys,
            fallback_series_keys=fallback_series_keys,
        )

        cadence_decisions: list[dict[str, object]] = []
        if self._trend_runtime_processor is not None:
            for series_key in series_keys_to_process:
                cadence_decision: object = None
                try:
                    trend_result = self._trend_runtime_processor.process_series(
                        series_key=series_key
                    )
                    cadence_decision = trend_result.get("cadence_decision")
                    normalized = _normalize_cadence_decision(
                        series_key=series_key,
                        cadence_decision=cadence_decision,
                    )
                    if normalized is not None:
                        cadence_decisions.append(normalized)
                except Exception as exc:  # pragma: no cover
                    raise TrendProcessingError(
                        f"trend processing failed for series={series_key}: {exc}"
                    ) from exc

                if _is_true_irregular_cadence_failure(cadence_decision):
                    raise TrendProcessingError(
                        "trend processing failed for series="
                        f"{series_key}: irregular_spacing {_cadence_reason_code(cadence_decision)}"
                    )

        status = _derive_status(
            accepted_count=accepted_count,
            quarantined_count=quarantined_count,
            failed_count=failed_count,
        )

        return SourceWorkflowResult(
            source_key=request.source_key,
            status=status,
            accepted_count=accepted_count,
            quarantined_count=quarantined_count,
            failed_count=failed_count,
            cadence_decisions=cadence_decisions,
        )
