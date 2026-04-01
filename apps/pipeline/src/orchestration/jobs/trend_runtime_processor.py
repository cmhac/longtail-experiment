"""Runtime trend processing integration for source-ingest execution paths."""

from __future__ import annotations

import importlib
import sys
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Any, cast

from .trend_backfill_service import decide_backfill_scope
from .trend_lifecycle_service import PersistedTrendSnapshot, TrendLifecycleService
from .trend_transition_logic import TrendAnalysisResultLike


def _ensure_trend_library_import_path() -> None:
    """Ensure local trend-analysis library source path is importable."""
    repo_root = Path(__file__).resolve().parents[5]
    trend_src = repo_root / "libs" / "trend_analysis" / "src"
    trend_src_str = str(trend_src)
    if trend_src_str not in sys.path:
        sys.path.insert(0, trend_src_str)


def _load_trend_library_symbols() -> tuple[Any, int, str]:
    """Load trend-analysis symbols used by runtime processing."""
    _ensure_trend_library_import_path()
    classifier_module = importlib.import_module("trend_analysis.classifier")
    version_module = importlib.import_module("trend_analysis.version")
    analyze_series = classifier_module.analyze_series
    min_required_observations = int(classifier_module.MIN_REQUIRED_OBSERVATIONS)
    library_version = str(version_module.LIBRARY_VERSION)
    return analyze_series, min_required_observations, library_version


_ANALYZE_SERIES, _MIN_REQUIRED_OBSERVATIONS, _LIBRARY_VERSION = _load_trend_library_symbols()


class TrendRuntimeProcessor:
    """Execute trend classification and lifecycle persistence for updated series."""

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

    def process_series(self, *, series_key: str) -> dict[str, object]:
        """Process trend updates for one series after observation persistence."""
        rows = self._observation_repository.read_series_observations(series_key=series_key)
        if not rows:
            return {
                "series_key": series_key,
                "execution_state": "no_op",
                "outcome_reason_code": "no_observations",
            }

        points = [
            (
                cast(date, row["observed_on"]),
                float(row["value"]),
            )
            for row in rows
        ]

        existing_count = self._trend_repository.count_trend_records_for_series(
            series_key=series_key
        )
        has_sufficient_history = len(points) >= _MIN_REQUIRED_OBSERVATIONS
        backfill_decision = decide_backfill_scope(
            existing_trend_record_count=existing_count,
            has_sufficient_history=has_sufficient_history,
        )

        if backfill_decision.run_full_backfill:
            return self._run_full_backfill(series_key=series_key, points=points)

        return self._run_single_pass(series_key=series_key, points=points)

    def _run_full_backfill(
        self,
        *,
        series_key: str,
        points: list[tuple[date, float]],
    ) -> dict[str, object]:
        """Run deterministic full-history lifecycle processing for a series."""
        if len(points) < _MIN_REQUIRED_OBSERVATIONS:
            return {
                "series_key": series_key,
                "execution_state": "no_op",
                "outcome_reason_code": "insufficient_history_forward_only",
            }

        last_reason = "no_significant_trend"
        for index in range(_MIN_REQUIRED_OBSERVATIONS, len(points) + 1):
            segment = points[:index]
            analysis_result = cast(TrendAnalysisResultLike, _ANALYZE_SERIES(segment))
            latest_period = segment[-1][0]
            latest_observation_on = datetime.combine(latest_period, time.min, tzinfo=UTC)
            existing = self._read_existing_snapshot(series_key=series_key)
            result = self._lifecycle_service.apply_analysis_result(
                series_key=series_key,
                latest_observation_on=latest_observation_on,
                analysis_result=analysis_result,
                existing_trend=existing,
            )
            last_reason = result.outcome_reason_code

        return {
            "series_key": series_key,
            "execution_state": "applied",
            "outcome_reason_code": "first_run_full_backfill",
            "final_transition_reason": last_reason,
        }

    def _run_single_pass(
        self,
        *,
        series_key: str,
        points: list[tuple[date, float]],
    ) -> dict[str, object]:
        """Run single-pass trend processing for already-initialized series."""
        analysis_result = cast(TrendAnalysisResultLike, _ANALYZE_SERIES(points))
        latest_period = points[-1][0]
        latest_observation_on = datetime.combine(latest_period, time.min, tzinfo=UTC)
        existing = self._read_existing_snapshot(series_key=series_key)

        result = self._lifecycle_service.apply_analysis_result(
            series_key=series_key,
            latest_observation_on=latest_observation_on,
            analysis_result=analysis_result,
            existing_trend=existing,
        )
        return {
            "series_key": series_key,
            "execution_state": result.outcome_state,
            "outcome_reason_code": result.outcome_reason_code,
        }

    def _read_existing_snapshot(self, *, series_key: str) -> PersistedTrendSnapshot | None:
        """Read current ongoing trend snapshot for continuity decisions."""
        row = self._trend_repository.get_ongoing_trend_for_series(series_key=series_key)
        if row is None:
            return None

        return PersistedTrendSnapshot(
            trend_record_id=str(row["id"]),
            trend_label=str(row["trend_label"]),
            direction=str(row["direction"]),
            strength=str(row["strength"]),
            seasonality_classification=str(row["seasonality_classification"]),
            analysis_version=_LIBRARY_VERSION,
        )
