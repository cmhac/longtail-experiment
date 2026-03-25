"""Contract models for recent dataset updates query responses."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .dataset_search_query import DatasetSummary


class DatasetRecentActionLinks(BaseModel):
    """Action destinations exposed for editorial feed rows."""

    view_table_href: str = Field(min_length=1)
    download_csv_href: str = Field(min_length=1)


class DatasetRecentItem(DatasetSummary):
    """Recent item payload for homepage editorial feed rows."""

    action_links: DatasetRecentActionLinks


class DatasetRecentUpdatesResponse(BaseModel):
    """Recent updates response for landing page feed."""

    items: list[DatasetRecentItem]
    limit: int = Field(ge=1, le=5)
    sort: str = Field(min_length=1)
