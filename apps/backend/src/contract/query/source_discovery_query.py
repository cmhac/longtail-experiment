"""Contract models for source discovery query responses."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .dataset_search_query import DatasetSummary, SourceRef


class SourceSummary(BaseModel):
    """Summary record for one discoverable source."""

    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    dataset_count: int = Field(ge=0)
    source_type: str | None = None


class SourceListResponse(BaseModel):
    """List payload for discoverable sources."""

    items: list[SourceSummary]
    total_items: int = Field(ge=0)
    sort: str = Field(min_length=1)


class SourceDetailResponse(BaseModel):
    """Detail payload for one source and its datasets."""

    source: SourceSummary
    items: list[DatasetSummary]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    sort: str = Field(min_length=1)


class SourceNotFoundResponse(BaseModel):
    """Optional response envelope docs helper for source not found."""

    error: SourceRef
