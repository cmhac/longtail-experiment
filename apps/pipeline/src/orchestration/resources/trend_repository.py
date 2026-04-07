"""Structural contracts for trend lifecycle persistence resources."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Protocol, TypedDict


class TrendRecordInsert(TypedDict):
    """Values needed to persist one lifecycle trend record."""

    series_key: str
    trend_label: str
    direction: str
    strength: str
    seasonality_classification: str
    start_period: datetime
    end_period: datetime | None
    is_ongoing: bool


class TrendTransitionInsert(TypedDict):
    """Values needed to persist one lifecycle transition event."""

    series_key: str
    transition_type: str
    prior_trend_record_id: str | None
    new_trend_record_id: str | None
    trigger_observation_on: datetime
    reason: str


class LookbackApplicabilityInsert(TypedDict):
    """Values needed to persist one lookback applicability evaluation row."""

    series_key: str
    observed_on: date
    observation_id: str | None
    lookback_points: int
    applicability_state: Literal["applicable", "inapplicable"]
    reason_code: str
    reason_detail: str | None


class LookbackSnapshotInsert(TypedDict):
    """Values needed to persist one lookback trend snapshot row."""

    series_key: str
    observed_on: date
    observation_id: str | None
    lookback_points: int
    outcome_state: Literal["significant_trend", "no_significant_trend"]
    descriptor_state: Literal["available", "unavailable"]
    trend_label: str | None
    direction: Literal["up", "down", "flat"] | None
    confidence_score: float | None
    dominant_measure_family: Literal["theil_sen", "mixed", "none"]
    theil_sen_slope: float | None
    theil_sen_low_slope: float | None
    theil_sen_high_slope: float | None
    kendall_tau: float | None
    kendall_pvalue: float | None
    ols_slope: float | None
    ols_intercept: float | None
    ols_r_squared: float | None
    ols_pvalue: float | None
    preprocessing: dict[str, object] | None
    reason_code: str | None
    strength: str | None
    seasonality_classification: str | None
    analysis_version: str


class CanonicalDescriptorInsert(TypedDict):
    """Values needed to persist one canonical trend descriptor snapshot row."""

    series_key: str
    observed_on: date
    observation_id: str | None
    descriptor_version: Literal["v2"]
    descriptor_state: Literal["available", "unavailable"]
    canonical_trend_label: str | None
    canonical_direction: Literal["up", "down", "flat"] | None
    confidence_score: float | None
    dominant_measure_family: Literal["theil_sen", "mixed", "none"]
    medium_horizon_weight: float | None
    short_horizon_weight: float | None
    long_horizon_weight: float | None
    preprocessing: dict[str, object] | None
    ols_slope: float | None
    ols_intercept: float | None
    ols_r_squared: float | None
    ols_pvalue: float | None
    reason_code: str | None
    canonical_strength: str | None
    selected_lookback_points: int | None
    weighting_version: str
    weighting_trace: dict[str, object] | None


class TrendChangeEventInsert(TypedDict):
    """Values needed to persist one idempotent trend-change event row."""

    series_key: str
    previous_direction: Literal["up", "down"]
    current_direction: Literal["up", "down"]
    effective_observed_on: date
    processing_context: Literal["incremental", "historical_reprocessing"]
    visibility_classification: Literal["user_visible", "audit_only"]
    idempotency_fingerprint: str
    emitted_at: datetime


class TrendRepository(Protocol):
    """Persistence contract for trend lifecycle records/events."""

    def get_ongoing_trend_for_series(self, *, series_key: str) -> dict[str, object] | None:
        """Return current ongoing trend snapshot for one series, if present."""
        ...

    def upsert_trend_record(self, payload: TrendRecordInsert) -> str:
        """Insert or update one trend record and return canonical record id."""
        ...

    def close_ongoing_trend_for_series(
        self,
        *,
        series_key: str,
        end_period: datetime,
    ) -> str | None:
        """Mark the current ongoing trend as ended and return its id when present."""
        ...

    def append_transition(self, payload: TrendTransitionInsert) -> None:
        """Persist one transition event for auditing and downstream visibility."""
        ...

    def count_trend_records_for_series(self, *, series_key: str) -> int:
        """Return persisted trend record count for one canonical series key."""
        ...

    def count_canonical_descriptors_for_series(self, *, series_key: str) -> int:
        """Return persisted canonical descriptor count for one canonical series key."""
        ...

    def upsert_lookback_applicability(self, payload: LookbackApplicabilityInsert) -> None:
        """Persist one applicability decision for a series at one observation lookback."""
        ...

    def upsert_lookback_snapshot(self, payload: LookbackSnapshotInsert) -> None:
        """Persist one per-lookback trend outcome snapshot for a series observation."""
        ...

    def upsert_canonical_descriptor(self, payload: CanonicalDescriptorInsert) -> None:
        """Persist one weighted canonical descriptor snapshot for a series observation."""
        ...

    def get_previous_canonical_direction(
        self,
        *,
        series_key: str,
        observed_on: date,
    ) -> Literal["up", "down"] | None:
        """Return latest persisted canonical direction before observed date when present."""
        ...

    def append_trend_change_event(self, payload: TrendChangeEventInsert) -> dict[str, object]:
        """Persist one trend-change event idempotently and return event metadata."""
        ...

    def fan_out_notifications_for_event(self, *, event_id: str) -> int:
        """Fan out one user-visible trend event to active subscriptions."""
        ...
