"""Per-series downstream trend-processing execution helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from .trend_lifecycle_service import TrendLookbackApplyResult


class TrendLookbackApplier(Protocol):
    """Structural protocol for applying lookback snapshot decisions."""

    def apply_lookback_evaluation(
        self,
        *,
        series_key: str,
        observed_on: date,
        observation_id: str | None,
        evaluation_result: object,
    ) -> TrendLookbackApplyResult:
        """Apply one lookback evaluation outcome to persistence."""


@dataclass(frozen=True)
class TrendProcessingMetadata:
    """Per-series metadata emitted from downstream trend-processing step."""

    series_key: str
    execution_state: str
    outcome_reason_code: str


UpdatedSeriesInput = tuple[str, date, str | None, object]


def process_one_series(
    *,
    series_key: str,
    observed_on: date,
    observation_id: str | None,
    evaluation_result: object,
    lookback_applier: TrendLookbackApplier,
) -> TrendProcessingMetadata:
    """Process one updated series and emit explicit metadata."""
    apply_result = lookback_applier.apply_lookback_evaluation(
        series_key=series_key,
        observed_on=observed_on,
        observation_id=observation_id,
        evaluation_result=evaluation_result,
    )
    return TrendProcessingMetadata(
        series_key=series_key,
        execution_state=apply_result.outcome_state,
        outcome_reason_code=apply_result.outcome_reason_code,
    )


def process_updated_series(
    *,
    updated_series: list[UpdatedSeriesInput],
    lookback_applier: TrendLookbackApplier,
) -> list[TrendProcessingMetadata]:
    """Execute downstream trend processing per updated series in deterministic order."""
    metadata: list[TrendProcessingMetadata] = []
    for series_key, observed_on, observation_id, evaluation_result in updated_series:
        metadata.append(
            process_one_series(
                series_key=series_key,
                observed_on=observed_on,
                observation_id=observation_id,
                evaluation_result=evaluation_result,
                lookback_applier=lookback_applier,
            )
        )
    return metadata
