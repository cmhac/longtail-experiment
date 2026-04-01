"""Per-series downstream trend-processing execution helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from .trend_lifecycle_service import PersistedTrendSnapshot, TrendLifecycleApplyResult
from .trend_transition_logic import TrendAnalysisResultLike


class TrendLifecycleApplier(Protocol):
    """Structural protocol for applying trend lifecycle decisions."""

    def apply_analysis_result(
        self,
        *,
        series_key: str,
        latest_observation_on: datetime,
        analysis_result: TrendAnalysisResultLike,
        existing_trend: PersistedTrendSnapshot | None,
    ) -> TrendLifecycleApplyResult:
        """Apply one analysis outcome to trend lifecycle persistence."""


@dataclass(frozen=True)
class TrendProcessingMetadata:
    """Per-series metadata emitted from downstream trend-processing step."""

    series_key: str
    execution_state: str
    outcome_reason_code: str


UpdatedSeriesInput = tuple[
    str,
    datetime,
    TrendAnalysisResultLike,
    PersistedTrendSnapshot | None,
]


def process_one_series(
    *,
    series_key: str,
    latest_observation_on: datetime,
    analysis_result: TrendAnalysisResultLike,
    existing_trend: PersistedTrendSnapshot | None,
    lifecycle_applier: TrendLifecycleApplier,
) -> TrendProcessingMetadata:
    """Process one updated series and emit explicit no-op/applied metadata."""
    apply_result = lifecycle_applier.apply_analysis_result(
        series_key=series_key,
        latest_observation_on=latest_observation_on,
        analysis_result=analysis_result,
        existing_trend=existing_trend,
    )
    return TrendProcessingMetadata(
        series_key=series_key,
        execution_state=apply_result.outcome_state,
        outcome_reason_code=apply_result.outcome_reason_code,
    )


def process_updated_series(
    *,
    updated_series: list[UpdatedSeriesInput],
    lifecycle_applier: TrendLifecycleApplier,
) -> list[TrendProcessingMetadata]:
    """Execute downstream trend processing per updated series in deterministic order."""
    metadata: list[TrendProcessingMetadata] = []
    for series_key, latest_observation_on, analysis_result, existing_trend in updated_series:
        metadata.append(
            process_one_series(
                series_key=series_key,
                latest_observation_on=latest_observation_on,
                analysis_result=analysis_result,
                existing_trend=existing_trend,
                lifecycle_applier=lifecycle_applier,
            )
        )
    return metadata
