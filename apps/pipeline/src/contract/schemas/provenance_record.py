"""US2 provenance schema with immutability guarantees."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProvenanceRecord(BaseModel):
    """Immutable provenance metadata bound to one accepted observation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    observation_id: str = Field(min_length=1)
    source_release_id: str = Field(min_length=1)
    source_document_ref: str = Field(min_length=1)
    source_published_at: datetime
    source_retrieval_at: datetime
    ingest_run_id: str = Field(min_length=1)
    acquisition_method: str = Field(min_length=1)
    immutable_flag: bool = True
