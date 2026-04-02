"""Contract tests for trend repository protocol payloads and method surface."""

from __future__ import annotations

import sys
from datetime import UTC, date, datetime
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.resources.trend_repository import (
    CanonicalDescriptorInsert,
    LookbackApplicabilityInsert,
    LookbackSnapshotInsert,
    TrendRecordInsert,
    TrendRepository,
    TrendTransitionInsert,
)

EXPECTED_LOOKBACK_POINTS = 12

REQUIRED_METHOD_NAMES = (
    "get_ongoing_trend_for_series",
    "upsert_trend_record",
    "close_ongoing_trend_for_series",
    "append_transition",
    "count_trend_records_for_series",
    "upsert_lookback_applicability",
    "upsert_lookback_snapshot",
    "upsert_canonical_descriptor",
)


class FakeTrendRepository(TrendRepository):
    """In-memory fake implementing the trend repository protocol surface."""

    def __init__(self) -> None:
        """Initialize capture buffers for assertion-friendly protocol tests."""
        self.ongoing_by_series: dict[str, dict[str, object]] = {}
        self.record_writes: list[TrendRecordInsert] = []
        self.transition_writes: list[TrendTransitionInsert] = []
        self.lookback_applicability_writes: list[LookbackApplicabilityInsert] = []
        self.lookback_snapshot_writes: list[LookbackSnapshotInsert] = []
        self.canonical_descriptor_writes: list[CanonicalDescriptorInsert] = []

    def get_ongoing_trend_for_series(self, *, series_key: str) -> dict[str, object] | None:
        """Return one stored ongoing record for a series when present."""
        return self.ongoing_by_series.get(series_key)

    def upsert_trend_record(self, payload: TrendRecordInsert) -> str:
        """Capture one lifecycle record write and return a stable synthetic id."""
        self.record_writes.append(payload)
        record_id = f"trend-record-{len(self.record_writes)}"
        if payload["is_ongoing"]:
            self.ongoing_by_series[payload["series_key"]] = {
                "id": record_id,
                "trend_label": payload["trend_label"],
                "direction": payload["direction"],
                "strength": payload["strength"],
                "seasonality_classification": payload["seasonality_classification"],
            }
        return record_id

    def close_ongoing_trend_for_series(
        self,
        *,
        series_key: str,
        end_period: datetime,
    ) -> str | None:
        """Mark one stored ongoing trend closed and return its record id when present."""
        ongoing = self.ongoing_by_series.pop(series_key, None)
        if ongoing is None:
            return None
        ongoing["end_period"] = end_period
        return str(ongoing["id"])

    def append_transition(self, payload: TrendTransitionInsert) -> None:
        """Capture one transition write for audit assertions."""
        self.transition_writes.append(payload)

    def count_trend_records_for_series(self, *, series_key: str) -> int:
        """Return count of captured trend-record writes for one series key."""
        return sum(1 for write in self.record_writes if write["series_key"] == series_key)

    def upsert_lookback_applicability(self, payload: LookbackApplicabilityInsert) -> None:
        """Capture one lookback applicability write."""
        self.lookback_applicability_writes.append(payload)

    def upsert_lookback_snapshot(self, payload: LookbackSnapshotInsert) -> None:
        """Capture one lookback snapshot write."""
        self.lookback_snapshot_writes.append(payload)

    def upsert_canonical_descriptor(self, payload: CanonicalDescriptorInsert) -> None:
        """Capture one canonical descriptor write."""
        self.canonical_descriptor_writes.append(payload)


def test_fake_repository_overrides_full_protocol_surface() -> None:
    """Fake repositories should explicitly implement lifecycle and new methods."""
    missing = [name for name in REQUIRED_METHOD_NAMES if name not in FakeTrendRepository.__dict__]
    assert missing == []


def test_protocol_surface_supports_lifecycle_and_snapshot_payloads() -> None:
    """Protocol consumers should use lifecycle and new snapshot methods together."""
    repository: TrendRepository = FakeTrendRepository()
    observed_on = date(2026, 3, 1)
    observed_at = datetime(2026, 3, 1, tzinfo=UTC)

    record_id = repository.upsert_trend_record(
        TrendRecordInsert(
            series_key="SERIES.T009",
            trend_label="mild_sustained_uptrend",
            direction="up",
            strength="mild",
            seasonality_classification="non_seasonal",
            start_period=observed_at,
            end_period=None,
            is_ongoing=True,
        )
    )
    repository.append_transition(
        TrendTransitionInsert(
            series_key="SERIES.T009",
            transition_type="start",
            prior_trend_record_id=None,
            new_trend_record_id=record_id,
            trigger_observation_on=observed_at,
            reason="new_significant_trend",
        )
    )
    repository.upsert_lookback_applicability(
        LookbackApplicabilityInsert(
            series_key="SERIES.T009",
            observed_on=observed_on,
            observation_id=None,
            lookback_points=EXPECTED_LOOKBACK_POINTS,
            applicability_state="applicable",
            reason_code="enough_observations",
            reason_detail=None,
        )
    )
    repository.upsert_lookback_snapshot(
        LookbackSnapshotInsert(
            series_key="SERIES.T009",
            observed_on=observed_on,
            observation_id=None,
            lookback_points=EXPECTED_LOOKBACK_POINTS,
            outcome_state="significant_trend",
            trend_label="mild_sustained_uptrend",
            direction="up",
            strength="mild",
            seasonality_classification="non_seasonal",
            analysis_version="0.2.0",
        )
    )
    repository.upsert_canonical_descriptor(
        CanonicalDescriptorInsert(
            series_key="SERIES.T009",
            observed_on=observed_on,
            observation_id=None,
            descriptor_state="available",
            canonical_trend_label="mild_sustained_uptrend",
            canonical_direction="up",
            canonical_strength="mild",
            selected_lookback_points=EXPECTED_LOOKBACK_POINTS,
            weighting_version="1.0.0",
            weighting_trace=cast(dict[str, object], {"12": 0.95}),
        )
    )

    assert repository.count_trend_records_for_series(series_key="SERIES.T009") == 1
    assert repository.get_ongoing_trend_for_series(series_key="SERIES.T009") is not None
    assert (
        repository.close_ongoing_trend_for_series(
            series_key="SERIES.T009",
            end_period=observed_at,
        )
        == "trend-record-1"
    )

    fake_repository = repository
    assert isinstance(fake_repository, FakeTrendRepository)
    assert len(fake_repository.transition_writes) == 1
    assert len(fake_repository.lookback_applicability_writes) == 1
    assert len(fake_repository.lookback_snapshot_writes) == 1
    assert len(fake_repository.canonical_descriptor_writes) == 1


def test_new_typed_dict_payload_keys_are_accessible() -> None:
    """Lookback and canonical typed-dict payload keys should be read safely."""
    applicability_payload = LookbackApplicabilityInsert(
        series_key="SERIES.KEYS",
        observed_on=date(2026, 2, 1),
        observation_id=None,
        lookback_points=EXPECTED_LOOKBACK_POINTS,
        applicability_state="inapplicable",
        reason_code="insufficient_points",
        reason_detail="need 24 points",
    )
    snapshot_payload = LookbackSnapshotInsert(
        series_key="SERIES.KEYS",
        observed_on=date(2026, 2, 1),
        observation_id=None,
        lookback_points=EXPECTED_LOOKBACK_POINTS,
        outcome_state="no_significant_trend",
        trend_label=None,
        direction=None,
        strength=None,
        seasonality_classification=None,
        analysis_version="0.2.0",
    )
    descriptor_payload = CanonicalDescriptorInsert(
        series_key="SERIES.KEYS",
        observed_on=date(2026, 2, 1),
        observation_id=None,
        descriptor_state="unavailable",
        canonical_trend_label=None,
        canonical_direction=None,
        canonical_strength=None,
        selected_lookback_points=None,
        weighting_version="1.0.0",
        weighting_trace=None,
    )

    assert applicability_payload["lookback_points"] == EXPECTED_LOOKBACK_POINTS
    assert applicability_payload["reason_code"] == "insufficient_points"
    assert snapshot_payload["outcome_state"] == "no_significant_trend"
    assert snapshot_payload["analysis_version"] == "0.2.0"
    assert descriptor_payload["descriptor_state"] == "unavailable"
    assert descriptor_payload["selected_lookback_points"] is None
