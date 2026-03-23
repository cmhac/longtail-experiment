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


class DatasetDetailResponse(BaseModel):
    """Dataset detail payload containing metadata and observations."""

    dataset_id: str = Field(min_length=1)
    source: SourceRef
    title: str = Field(min_length=1)
    description: str | None = None
    geographic_scope: str | None = None
    topic_tags: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)
    observations: list[DatasetObservationPoint] = Field(default_factory=list)
    observation_sort: str = Field(min_length=1)
