"""Contract models for dataset search query responses."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class SourceRef(BaseModel):
    """Source attribution for a dataset payload."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)


class SummaryCanonicalTrendDescriptor(BaseModel):
    """Canonical trend descriptor payload for dataset summary/list responses."""

    descriptor_version: Literal["v2"] = "v2"
    descriptor_state: Literal["available", "unavailable"]
    trend_label: str | None = Field(default=None, min_length=1)
    direction: Literal["up", "down", "flat"] | None = None
    confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    dominant_measure_family: Literal["theil_sen", "mixed", "none"] = "none"
    strength: str | None = Field(default=None, min_length=1)
    selected_lookback_points: int | None = Field(default=None, ge=1)
    observed_on: str | None = Field(default=None, min_length=1)
    reason_code: str | None = Field(default=None, min_length=1)


class DatasetSummary(BaseModel):
    """Discovery card summary for search and catalog workflows."""

    dataset_id: str = Field(min_length=1)
    source: SourceRef
    title: str = Field(min_length=1)
    description: str | None = None
    geographic_scope: str | None = None
    topic_tags: list[str] = Field(default_factory=list)
    latest_update_at: str | None = None
    canonical_trend_descriptor: SummaryCanonicalTrendDescriptor


class DatasetSearchResponse(BaseModel):
    """Paginated dataset search response payload."""

    items: list[DatasetSummary]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    sort: str = Field(min_length=1)


class SearchScopeSummaryResponse(BaseModel):
    """Aggregate summary payload for homepage search scope text."""

    active_dataset_count: int = Field(ge=0)
    active_source_count: int = Field(ge=0)
    generated_at: str | None = None


class SuggestionItem(BaseModel):
    """One likely-match suggestion item for incremental search."""

    dataset_id: str = Field(min_length=1)
    source: SourceRef
    title: str = Field(min_length=1)
    rank_score: float


class DatasetSearchSuggestionsResponse(BaseModel):
    """Likely-match suggestion payload for one search query."""

    query: str = Field(min_length=1)
    limit: int = Field(ge=1)
    items: list[SuggestionItem]
