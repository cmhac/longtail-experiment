"""Contract models for dataset detail query responses."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .dataset_search_query import SourceRef


class DatasetObservationPoint(BaseModel):
    """One observation returned in dataset detail payloads."""

    observed_on: str = Field(min_length=1)
    value: float
    reported_at: str = Field(min_length=1)
    attributes: dict[str, object] = Field(default_factory=dict)

class CanonicalTrendDescriptor(BaseModel):
    """Canonical trend descriptor payload for dataset detail responses."""

    descriptor_state: str = Field(min_length=1)
    trend_label: str | None = Field(default=None, min_length=1)
    direction: str | None = Field(default=None, min_length=1)
    strength: str | None = Field(default=None, min_length=1)
    selected_lookback_points: int | None = Field(default=None, ge=1)
    observed_on: str | None = Field(default=None, min_length=1)
    reason_code: str | None = Field(default=None, min_length=1)


class LookbackTrendSnapshot(BaseModel):
    """Per-lookback trend snapshot payload for dataset detail responses."""

    lookback_points: int = Field(ge=1)
    applicability_state: str = Field(min_length=1)
    outcome_state: str | None = Field(default=None, min_length=1)
    trend_label: str | None = Field(default=None, min_length=1)
    direction: str | None = Field(default=None, min_length=1)
    strength: str | None = Field(default=None, min_length=1)
    reason_code: str | None = Field(default=None, min_length=1)


class DatasetDetailQueryResult(BaseModel):
    """Dataset detail query payload containing metadata and observations."""

    dataset_id: str = Field(min_length=1)
    source: SourceRef
    title: str = Field(min_length=1)
    description: str | None = None
    geographic_scope: str | None = None
    topic_tags: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)
    observations: list[DatasetObservationPoint] = Field(default_factory=list)
    canonical_trend_descriptor: CanonicalTrendDescriptor
    lookback_trend_snapshots: list[LookbackTrendSnapshot] = Field(default_factory=list)
    observation_sort: str = Field(min_length=1)


class DatasetDetailResponse(DatasetDetailQueryResult):
    """Backward-compatible dataset detail response model."""
