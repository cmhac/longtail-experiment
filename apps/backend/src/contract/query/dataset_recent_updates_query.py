"""Contract models for recent dataset updates query responses."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .dataset_search_query import DatasetSummary


class DatasetRecentActionLinks(BaseModel):
    """Action destinations exposed for editorial feed rows."""

    view_table_href: str = Field(min_length=1)
    download_csv_href: str = Field(min_length=1)


class DatasetRecentItem(DatasetSummary):
    """Recent item payload for homepage editorial feed rows."""

    item_type: Literal["dataset_update"] = "dataset_update"
    has_recent_notification: bool = False

    action_links: DatasetRecentActionLinks


class TrendRecentItem(BaseModel):
    """Recent item payload for trend lifecycle events in unified feed."""

    item_type: Literal["trend_event"] = "trend_event"
    dataset_id: str = Field(min_length=1)
    source: dict[str, str] = Field(default_factory=dict)
    title: str = Field(min_length=1)
    direction: str = Field(min_length=1)
    strength: str = Field(min_length=1)
    start_period: str = Field(min_length=1)
    latest_update_at: str = Field(min_length=1)
    action_links: DatasetRecentActionLinks


class DatasetRecentUpdatesResponse(BaseModel):
    """Recent updates response for landing page feed."""

    items: list[DatasetRecentItem | TrendRecentItem]
    limit: int = Field(ge=1, le=5)
    sort: str = Field(min_length=1)
