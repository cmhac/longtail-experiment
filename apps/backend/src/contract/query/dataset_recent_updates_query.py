"""Contract models for recent dataset updates query responses."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .dataset_search_query import DatasetSummary


class DatasetRecentUpdatesResponse(BaseModel):
    """Recent updates response for landing page feed."""

    items: list[DatasetSummary]
    limit: int = Field(ge=1, le=5)
    sort: str = Field(min_length=1)
