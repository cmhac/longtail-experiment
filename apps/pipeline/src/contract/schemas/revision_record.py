"""US2 revision schema enforcing lineage constraints."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, model_validator


class RevisionRecord(BaseModel):
    """Explicit link between superseded and current observation versions."""

    superseded_observation_id: str = Field(min_length=1)
    current_observation_id: str = Field(min_length=1)
    revision_reason: str = Field(min_length=1)
    series_key: str = Field(min_length=1)
    reference_period_start: date
    reference_period_end: date

    @model_validator(mode="after")
    def _validate_lineage(self) -> RevisionRecord:
        if self.superseded_observation_id == self.current_observation_id:
            raise ValueError("superseded and current observation ids must differ")
        if self.reference_period_start > self.reference_period_end:
            raise ValueError("reference period start must be <= reference period end")
        return self
