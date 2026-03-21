"""Canonical observation schema and validation rules."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CanonicalObservation(BaseModel):
    """Normalized canonical observation used by ingest and query services."""

    model_config = ConfigDict(extra="forbid")

    source_name: str = Field(min_length=1)
    source_type: str = Field(pattern="^(external|internal)$")
    series_key: str = Field(min_length=1)
    metric_name: str = Field(min_length=1)
    frequency_granularity: str = Field(pattern="^(daily|weekly|monthly|quarterly|yearly)$")
    observed_on: date
    reported_at: datetime
    value: Decimal
    unit: str | None = None
    attributes: dict[str, str] = Field(default_factory=dict)
