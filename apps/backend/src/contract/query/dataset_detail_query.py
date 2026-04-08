"""Contract models for dataset detail query responses."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .dataset_search_query import SourceRef
from .trend_descriptor_v2 import CanonicalTrendDescriptorV2, LookbackTrendEvidenceV2


class DatasetObservationPoint(BaseModel):
    """One observation returned in dataset detail payloads."""

    observed_on: str = Field(min_length=1)
    value: float
    reported_at: str = Field(min_length=1)
    attributes: dict[str, object] = Field(default_factory=dict)
    as_of_trend_descriptor: CanonicalTrendDescriptorV2


class DatasetDetailQueryResult(BaseModel):
    """Dataset detail payload containing metadata, observations, and v2 trend evidence."""

    dataset_id: str = Field(min_length=1)
    source: SourceRef
    title: str = Field(min_length=1)
    description: str | None = None
    geographic_scope: str | None = None
    topic_tags: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)
    observations: list[DatasetObservationPoint] = Field(default_factory=list)
    canonical_trend_descriptor: CanonicalTrendDescriptorV2
    has_recent_notification: bool = False
    lookback_trend_evidence: list[LookbackTrendEvidenceV2] = Field(default_factory=list)
    observation_sort: str = Field(min_length=1)


class DatasetDetailResponse(DatasetDetailQueryResult):
    """Backward-compatible dataset detail response model."""
