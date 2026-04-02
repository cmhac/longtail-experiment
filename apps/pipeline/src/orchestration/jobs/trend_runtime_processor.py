"""Runtime trend processing integration for source-ingest execution paths."""

from __future__ import annotations

import importlib
import sys
from datetime import date
from pathlib import Path
from typing import Any, cast

from .trend_lifecycle_service import TrendLifecycleService


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
    return classifier_module.evaluate_multi_lookbacks


_EVALUATE_MULTI_LOOKBACKS = _load_trend_library_symbols()


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

    def process_series(self, *, series_key: str) -> dict[str, object]:
        """Process lookback snapshots and canonical descriptor for one series."""
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
        latest_observed_on = points[-1][0]
        latest_observation_id = rows[-1].get("observation_id")
        observation_id = str(latest_observation_id) if latest_observation_id is not None else None

        evaluation = _EVALUATE_MULTI_LOOKBACKS(points)

        apply_result = self._lifecycle_service.apply_lookback_evaluation(
            series_key=series_key,
            observed_on=latest_observed_on,
            observation_id=observation_id,
            evaluation_result=evaluation,
        )
        return {
            "series_key": series_key,
            "execution_state": apply_result.outcome_state,
            "outcome_reason_code": apply_result.outcome_reason_code,
        }
