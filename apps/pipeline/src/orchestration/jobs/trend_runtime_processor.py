"""Runtime trend processing integration for source-ingest execution paths."""

from __future__ import annotations

import importlib
import sys
from datetime import date
from pathlib import Path
from typing import Any, cast

from .trend_backfill_service import decide_backfill_scope
from .trend_lifecycle_service import TrendLifecycleService
from .trend_notification_service import TrendNotificationService


def _ensure_trend_library_import_path() -> None:
    """Ensure local trend-analysis library source path is importable."""
    repo_root = Path(__file__).resolve().parents[5]
    trend_src = repo_root / "libs" / "trend_analysis" / "src"
    trend_src_str = str(trend_src)
    if trend_src_str not in sys.path:
        sys.path.insert(0, trend_src_str)


def _load_trend_library_symbols() -> Any:
    """Load trend-analysis symbols used by runtime processing."""
    _ensure_trend_library_import_path()
    classifier_module = importlib.import_module("trend_analysis.classifier")
    cadence_module = importlib.import_module("trend_analysis.cadence")
    return (classifier_module.evaluate_multi_lookbacks, cadence_module.infer_cadence_decision)


_EVALUATE_MULTI_LOOKBACKS, _INFER_CADENCE_DECISION = _load_trend_library_symbols()
MIN_POINTS_FOR_CADENCE_INFERENCE = 3


def _serialize_cadence_decision(decision: object) -> dict[str, object]:
    """Convert cadence decision objects into JSON-safe runtime payloads."""
    return {
        "cadence_state": decision.cadence_state,
        "inferred_cadence": decision.inferred_cadence,
        "irregular_gap_count": decision.irregular_gap_count,
        "total_interval_count": decision.total_interval_count,
        "irregular_gap_ratio": decision.irregular_gap_ratio,
        "reason_code": decision.reason_code,
        "reason_detail": decision.reason_detail,
    }


class TrendRuntimeProcessor:
    """Execute trend classification and lookback persistence for updated series."""

    def __init__(
        self,
        *,
        observation_repository: Any,
        trend_repository: Any,
    ) -> None:
        """Initialize runtime processor with observation/trend repositories."""
        self._observation_repository = observation_repository
        self._trend_repository = trend_repository
        self._lifecycle_service = TrendLifecycleService(repository=trend_repository)
        self._notification_service = TrendNotificationService(repository=trend_repository)

    def process_series(self, *, series_key: str) -> dict[str, object]:
        """Process lookback snapshots and canonical descriptor for one series."""
        rows = self._observation_repository.read_series_observations(series_key=series_key)
        if not rows:
            return {
                "series_key": series_key,
                "execution_state": "no_op",
                "outcome_reason_code": "no_observations",
            }

        existing_trend_record_count = 0
        if hasattr(self._trend_repository, "count_trend_records_for_series"):
            existing_trend_record_count = int(
                self._trend_repository.count_trend_records_for_series(series_key=series_key)
            )
        existing_canonical_count: int | None = None
        if hasattr(self._trend_repository, "count_canonical_descriptors_for_series"):
            existing_canonical_count = int(
                self._trend_repository.count_canonical_descriptors_for_series(series_key=series_key)
            )

        eligible_observation_count = max(len(rows) - (MIN_POINTS_FOR_CADENCE_INFERENCE - 1), 0)
        backfill_decision = decide_backfill_scope(
            existing_trend_record_count=existing_trend_record_count,
            has_sufficient_history=len(rows) >= MIN_POINTS_FOR_CADENCE_INFERENCE,
        )
        requires_historical_backfill = (
            existing_canonical_count is not None
            and existing_canonical_count < eligible_observation_count
        )
        run_full_backfill = backfill_decision.run_full_backfill or requires_historical_backfill

        points = [
            (
                cast(date, row["observed_on"]),
                float(row["value"]),
            )
            for row in rows
        ]
        series_cadence_decision = _INFER_CADENCE_DECISION(points)
        if series_cadence_decision.cadence_state == "irregular_rejected":
            return {
                "series_key": series_key,
                "execution_state": "no_op",
                "outcome_reason_code": "cadence_irregular_rejected",
                "cadence_decision": _serialize_cadence_decision(series_cadence_decision),
            }

        rows_to_process = [rows[-1]]
        if run_full_backfill:
            rows_to_process = rows[MIN_POINTS_FOR_CADENCE_INFERENCE - 1 :]

        apply_results = []
        for row in rows_to_process:
            observed_on = cast(date, row["observed_on"])
            observation_id_value = row.get("observation_id")
            observation_id = str(observation_id_value) if observation_id_value is not None else None

            history_points = [
                (candidate_observed_on, candidate_value)
                for candidate_observed_on, candidate_value in points
                if candidate_observed_on <= observed_on
            ]
            history_cadence_decision = _INFER_CADENCE_DECISION(history_points)
            if history_cadence_decision.cadence_state == "irregular_rejected":
                continue

            evaluation = _EVALUATE_MULTI_LOOKBACKS(history_points)
            apply_result = self._lifecycle_service.apply_lookback_evaluation(
                series_key=series_key,
                observed_on=observed_on,
                observation_id=observation_id,
                evaluation_result=evaluation,
            )
            apply_results.append(apply_result)

            canonical = evaluation.canonical_descriptor
            current_direction = self._lifecycle_service.resolve_notification_direction(
                descriptor_state=canonical.descriptor_state,
                direction=canonical.direction,
            )
            processing_context, visibility_classification = (
                self._lifecycle_service.classify_notification_visibility(
                    run_full_backfill=run_full_backfill
                )
            )
            self._notification_service.process_canonical_transition(
                series_key=series_key,
                observed_on=observed_on,
                current_direction=current_direction,
                processing_context=processing_context,
                visibility_classification=visibility_classification,
            )

        apply_result = apply_results[-1]
        return {
            "series_key": series_key,
            "execution_state": apply_result.outcome_state,
            "outcome_reason_code": apply_result.outcome_reason_code,
            "cadence_decision": apply_result.cadence_decision,
        }
