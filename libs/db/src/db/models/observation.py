"""Observation model for canonical values."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .data_series import DataSeries
    from .lineage import ProvenanceRecord, RevisionRecord


class Observation(Base):
    """Canonical observation persisted for backend consumption."""

    __tablename__ = "observations"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    series_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_series.id"), nullable=False
    )
    observed_on: Mapped[date] = mapped_column(Date, nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    attributes: Mapped[dict[str, str]] = mapped_column(
        JSONB, default=dict, nullable=False
    )

    series: Mapped["DataSeries"] = relationship(back_populates="observations")
    provenance_records: Mapped[list["ProvenanceRecord"]] = relationship(
        back_populates="observation"
    )
    superseded_by: Mapped[list["RevisionRecord"]] = relationship(
        foreign_keys="RevisionRecord.superseded_observation_id",
        back_populates="superseded_observation",
    )
    supersedes: Mapped[list["RevisionRecord"]] = relationship(
        foreign_keys="RevisionRecord.current_observation_id",
        back_populates="current_observation",
    )
