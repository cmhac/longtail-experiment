"""Contract models for dataset catalog query responses."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .dataset_search_query import DatasetSummary, SourceRef


class DatasetSourceGroup(BaseModel):
    """Source grouping projection for catalog responses."""

    source: SourceRef
    dataset_count: int = Field(ge=0)
    dataset_ids: list[str] = Field(default_factory=list)


class DatasetCatalogResponse(BaseModel):
    """Paginated dataset catalog response payload."""

    items: list[DatasetSummary]
    groups: list[DatasetSourceGroup] = Field(default_factory=list)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    sort: str = Field(min_length=1)
