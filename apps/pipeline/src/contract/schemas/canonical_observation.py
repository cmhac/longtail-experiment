"""Canonical observation schema and validation rules."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CanonicalObservation(BaseModel):
    """Normalized canonical observation used by ingest and query services."""

    model_config = ConfigDict(extra="forbid")

    source_key: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    source_title: str = Field(min_length=1)
    source_description: str = Field(min_length=1)
    source_type: str = Field(pattern="^(external|internal)$")
    series_key: str = Field(min_length=1)
    metric_name: str = Field(min_length=1)
    dataset_title: str | None = Field(default=None, min_length=1)
    dataset_description: str | None = Field(default=None, min_length=1)
    dataset_geographic_scope: str | None = Field(default=None, min_length=1)
    topic_tags: list[str] = Field(default_factory=list)
    observed_on: date
    reported_at: datetime
    value: Decimal
    unit: str | None = None
    unit_type: Literal["usd", "percent", "number"] | None = None
    attributes: dict[str, str] = Field(default_factory=dict)
