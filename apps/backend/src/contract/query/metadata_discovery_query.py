"""Contract models for topic and geography discovery query responses."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .dataset_search_query import DatasetSummary


class TopicSummary(BaseModel):
    """Summary record for one discoverable topic."""

    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    dataset_count: int = Field(ge=0)


class TopicDetailResponse(BaseModel):
    """Detail payload for one topic and its datasets."""

    topic: TopicSummary
    items: list[DatasetSummary]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    sort: str = Field(min_length=1)


class GeographySummary(BaseModel):
    """Summary record for one discoverable geography."""

    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    dataset_count: int = Field(ge=0)


class GeographyDetailResponse(BaseModel):
    """Detail payload for one geography and its datasets."""

    geography: GeographySummary
    items: list[DatasetSummary]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    sort: str = Field(min_length=1)
