"""Series metadata model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .observation import Observation
    from .source_profile import SourceProfile
    from .topic_tag import TopicTag
    from .trends import (
        TrendCanonicalDescriptor,
        TrendChangeEvent,
        TrendLookbackEvaluation,
        TrendLookbackSnapshot,
        TrendRecord,
        TrendTransitionEvent,
        UserDatasetSubscription,
        UserTrendNotification,
    )


class DataSeries(Base):
    """Represents a logical time series persisted in the contract store."""

    __tablename__ = "data_series"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    source_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("source_profiles.id"), nullable=False
    )
    series_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    geographic_scope: Mapped[str | None] = mapped_column(String(255), nullable=True)
    default_scale: Mapped[Decimal] = mapped_column(
        Numeric(10, 4), nullable=False, default=1
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    source_profile: Mapped["SourceProfile"] = relationship(back_populates="series")
    observations: Mapped[list["Observation"]] = relationship(back_populates="series")
    topic_tags: Mapped[list["TopicTag"]] = relationship(
        secondary="data_series_topic_tags", back_populates="data_series"
    )
    trend_records: Mapped[list["TrendRecord"]] = relationship(
        back_populates="data_series"
    )
    trend_transition_events: Mapped[list["TrendTransitionEvent"]] = relationship(
        back_populates="data_series"
    )
    trend_lookback_evaluations: Mapped[list["TrendLookbackEvaluation"]] = relationship(
        back_populates="data_series"
    )
    trend_lookback_snapshots: Mapped[list["TrendLookbackSnapshot"]] = relationship(
        back_populates="data_series"
    )
    trend_canonical_descriptors: Mapped[list["TrendCanonicalDescriptor"]] = (
        relationship(back_populates="data_series")
    )
    trend_change_events: Mapped[list["TrendChangeEvent"]] = relationship(
        back_populates="data_series"
    )
    user_dataset_subscriptions: Mapped[list["UserDatasetSubscription"]] = relationship(
        back_populates="data_series"
    )
    user_trend_notifications: Mapped[list["UserTrendNotification"]] = relationship(
        back_populates="data_series"
    )
