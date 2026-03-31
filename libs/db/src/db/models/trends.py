"""Trend lifecycle persistence models."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .data_series import DataSeries


class TrendRecord(Base):
    """Persist one bounded trend segment for a dataset series."""

    __tablename__ = "trend_records"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    data_series_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_series.id"), nullable=False
    )
    trend_label: Mapped[str] = mapped_column(String(64), nullable=False)
    direction: Mapped[str] = mapped_column(String(16), nullable=False)
    strength: Mapped[str] = mapped_column(String(32), nullable=False)
    seasonality_classification: Mapped[str] = mapped_column(String(32), nullable=False)
    start_period: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_period: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_ongoing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    data_series: Mapped["DataSeries"] = relationship(back_populates="trend_records")


class TrendTransitionEvent(Base):
    """Auditable event emitted when trend lifecycle transitions occur."""

    __tablename__ = "trend_transition_events"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    data_series_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_series.id"), nullable=False
    )
    transition_type: Mapped[str] = mapped_column(String(32), nullable=False)
    prior_trend_record_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trend_records.id"), nullable=True
    )
    new_trend_record_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trend_records.id"), nullable=True
    )
    trigger_observation_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    data_series: Mapped["DataSeries"] = relationship(
        back_populates="trend_transition_events"
    )
