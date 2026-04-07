"""Trend lifecycle persistence models."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .auth_management import UserAccount
    from .data_series import DataSeries
    from .observation import Observation


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


class TrendLookbackEvaluation(Base):
    """Store per-lookback applicability decisions for each observation."""

    __tablename__ = "trend_lookback_evaluations"
    __table_args__ = (
        UniqueConstraint(
            "data_series_id",
            "observation_id",
            "lookback_points",
            name="uq_trend_lookback_evaluations_series_observation_lookback",
        ),
        CheckConstraint(
            "lookback_points > 0",
            name="ck_trend_lookback_evaluations_lookback_points_positive",
        ),
        CheckConstraint(
            "applicability_state IN ('applicable', 'inapplicable')",
            name="ck_trend_lookback_evaluations_applicability_state",
        ),
        Index(
            "ix_trend_lookback_evaluations_series_observation",
            "data_series_id",
            "observation_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    data_series_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_series.id"), nullable=False
    )
    observation_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("observations.id"), nullable=False
    )
    lookback_points: Mapped[int] = mapped_column(Integer, nullable=False)
    applicability_state: Mapped[str] = mapped_column(String(16), nullable=False)
    reason_code: Mapped[str] = mapped_column(String(64), nullable=False)
    reason_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    data_series: Mapped["DataSeries"] = relationship(
        back_populates="trend_lookback_evaluations"
    )
    observation: Mapped["Observation"] = relationship()


class TrendLookbackSnapshot(Base):
    """Persist per-lookback trend outcomes for an observation."""

    __tablename__ = "trend_lookback_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "data_series_id",
            "observation_id",
            "lookback_points",
            name="uq_trend_lookback_snapshots_series_observation_lookback",
        ),
        CheckConstraint(
            "lookback_points > 0",
            name="ck_trend_lookback_snapshots_lookback_points_positive",
        ),
        CheckConstraint(
            "outcome_state IN ('significant_trend', 'no_significant_trend')",
            name="ck_trend_lookback_snapshots_outcome_state",
        ),
        CheckConstraint(
            "direction IS NULL OR direction IN ('up', 'down', 'flat')",
            name="ck_trend_lookback_snapshots_direction",
        ),
        CheckConstraint(
            "descriptor_state IN ('available', 'unavailable')",
            name="ck_trend_lookback_snapshots_descriptor_state",
        ),
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="ck_trend_lookback_snapshots_confidence_score",
        ),
        Index(
            "ix_trend_lookback_snapshots_series_observed_on",
            "data_series_id",
            "observed_on",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    data_series_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_series.id"), nullable=False
    )
    observation_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("observations.id"), nullable=False
    )
    observed_on: Mapped[date] = mapped_column(Date, nullable=False)
    lookback_points: Mapped[int] = mapped_column(Integer, nullable=False)
    outcome_state: Mapped[str] = mapped_column(String(32), nullable=False)
    descriptor_state: Mapped[str] = mapped_column(String(16), nullable=False)
    trend_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    direction: Mapped[str | None] = mapped_column(String(16), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    dominant_measure_family: Mapped[str | None] = mapped_column(
        String(16), nullable=True
    )
    theil_sen_slope: Mapped[float | None] = mapped_column(nullable=True)
    theil_sen_low_slope: Mapped[float | None] = mapped_column(nullable=True)
    theil_sen_high_slope: Mapped[float | None] = mapped_column(nullable=True)
    kendall_tau: Mapped[float | None] = mapped_column(nullable=True)
    kendall_pvalue: Mapped[float | None] = mapped_column(nullable=True)
    ols_slope: Mapped[float | None] = mapped_column(nullable=True)
    ols_intercept: Mapped[float | None] = mapped_column(nullable=True)
    ols_r_squared: Mapped[float | None] = mapped_column(nullable=True)
    ols_pvalue: Mapped[float | None] = mapped_column(nullable=True)
    preprocessing: Mapped[dict[str, object] | None] = mapped_column(
        JSONB, nullable=True
    )
    reason_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    strength: Mapped[str | None] = mapped_column(String(32), nullable=True)
    seasonality_classification: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )
    analysis_version: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    data_series: Mapped["DataSeries"] = relationship(
        back_populates="trend_lookback_snapshots"
    )
    observation: Mapped["Observation"] = relationship()


class TrendCanonicalDescriptor(Base):
    """Store canonical weighted trend descriptors per observation."""

    __tablename__ = "trend_canonical_descriptors"
    __table_args__ = (
        UniqueConstraint(
            "data_series_id",
            "observation_id",
            name="uq_trend_canonical_descriptors_series_observation",
        ),
        CheckConstraint(
            "descriptor_state IN ('available', 'unavailable')",
            name="ck_trend_canonical_descriptors_state",
        ),
        CheckConstraint(
            "canonical_direction IS NULL OR canonical_direction IN ('up', 'down', 'flat')",
            name="ck_trend_canonical_descriptors_direction",
        ),
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="ck_trend_canonical_descriptors_confidence_score",
        ),
        CheckConstraint(
            "selected_lookback_points IS NULL OR selected_lookback_points > 0",
            name="ck_trend_canonical_descriptors_selected_lookback_positive",
        ),
        Index(
            "ix_trend_canonical_descriptors_series_observed_on",
            "data_series_id",
            "observed_on",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    data_series_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_series.id"), nullable=False
    )
    observation_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("observations.id"), nullable=False
    )
    observed_on: Mapped[date] = mapped_column(Date, nullable=False)
    descriptor_version: Mapped[str] = mapped_column(String(8), nullable=False)
    descriptor_state: Mapped[str] = mapped_column(String(16), nullable=False)
    canonical_trend_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    canonical_direction: Mapped[str | None] = mapped_column(String(16), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    dominant_measure_family: Mapped[str | None] = mapped_column(
        String(16), nullable=True
    )
    medium_horizon_weight: Mapped[float | None] = mapped_column(nullable=True)
    short_horizon_weight: Mapped[float | None] = mapped_column(nullable=True)
    long_horizon_weight: Mapped[float | None] = mapped_column(nullable=True)
    preprocessing: Mapped[dict[str, object] | None] = mapped_column(
        JSONB, nullable=True
    )
    ols_slope: Mapped[float | None] = mapped_column(nullable=True)
    ols_intercept: Mapped[float | None] = mapped_column(nullable=True)
    ols_r_squared: Mapped[float | None] = mapped_column(nullable=True)
    ols_pvalue: Mapped[float | None] = mapped_column(nullable=True)
    reason_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    canonical_strength: Mapped[str | None] = mapped_column(String(32), nullable=True)
    selected_lookback_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weighting_version: Mapped[str] = mapped_column(String(64), nullable=False)
    weighting_trace: Mapped[dict[str, object] | None] = mapped_column(
        JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    data_series: Mapped["DataSeries"] = relationship(
        back_populates="trend_canonical_descriptors"
    )
    observation: Mapped["Observation"] = relationship()


class TrendChangeEvent(Base):
    """Persist one canonical up/down reversal event for downstream delivery."""

    __tablename__ = "trend_change_events"
    __table_args__ = (
        UniqueConstraint(
            "idempotency_fingerprint",
            name="uq_trend_change_events_idempotency_fingerprint",
        ),
        CheckConstraint(
            "previous_direction IN ('up', 'down')",
            name="ck_trend_change_events_previous_direction",
        ),
        CheckConstraint(
            "current_direction IN ('up', 'down')",
            name="ck_trend_change_events_current_direction",
        ),
        CheckConstraint(
            "processing_context IN ('incremental', 'historical_reprocessing')",
            name="ck_trend_change_events_processing_context",
        ),
        CheckConstraint(
            "visibility_classification IN ('user_visible', 'audit_only')",
            name="ck_trend_change_events_visibility_classification",
        ),
        Index(
            "ix_trend_change_events_series_observed_on",
            "data_series_id",
            "effective_observed_on",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    data_series_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_series.id"), nullable=False
    )
    previous_direction: Mapped[str] = mapped_column(String(16), nullable=False)
    current_direction: Mapped[str] = mapped_column(String(16), nullable=False)
    effective_observed_on: Mapped[date] = mapped_column(Date, nullable=False)
    processing_context: Mapped[str] = mapped_column(String(32), nullable=False)
    visibility_classification: Mapped[str] = mapped_column(String(16), nullable=False)
    idempotency_fingerprint: Mapped[str] = mapped_column(String(255), nullable=False)
    emitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    data_series: Mapped["DataSeries"] = relationship(
        back_populates="trend_change_events"
    )
    notifications: Mapped[list["UserTrendNotification"]] = relationship(
        back_populates="event"
    )


class UserDatasetSubscription(Base):
    """Persist per-user dataset subscription eligibility for notifications."""

    __tablename__ = "user_dataset_subscriptions"
    __table_args__ = (
        Index(
            "ix_user_dataset_subscriptions_user_active",
            "user_id",
            "unsubscribed_at",
        ),
        Index(
            "ix_user_dataset_subscriptions_series_active",
            "data_series_id",
            "unsubscribed_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    data_series_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("data_series.id", ondelete="CASCADE"),
        nullable=False,
    )
    subscribed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    unsubscribed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    data_series: Mapped["DataSeries"] = relationship(
        back_populates="user_dataset_subscriptions"
    )
    user: Mapped["UserAccount"] = relationship(back_populates="dataset_subscriptions")


class UserTrendNotification(Base):
    """Persist per-user in-app notification rows derived from reversal events."""

    __tablename__ = "user_trend_notifications"
    __table_args__ = (
        UniqueConstraint(
            "event_id",
            "user_id",
            name="uq_user_trend_notifications_event_user",
        ),
        CheckConstraint(
            "unread_state IN ('unread', 'read')",
            name="ck_user_trend_notifications_unread_state",
        ),
        CheckConstraint(
            "channel IN ('in_app')",
            name="ck_user_trend_notifications_channel",
        ),
        CheckConstraint(
            "delivery_status IN ('queued', 'delivered', 'failed', 'suppressed')",
            name="ck_user_trend_notifications_delivery_status",
        ),
        CheckConstraint(
            "(unread_state = 'unread' AND read_at IS NULL) OR "
            "(unread_state = 'read' AND read_at IS NOT NULL)",
            name="ck_user_trend_notifications_read_state",
        ),
        Index(
            "ix_user_trend_notifications_user_delivery",
            "user_id",
            "delivered_at",
            "id",
        ),
        Index(
            "ix_user_trend_notifications_user_unread",
            "user_id",
            "unread_state",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    event_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trend_change_events.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    data_series_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("data_series.id", ondelete="CASCADE"),
        nullable=False,
    )
    destination_path: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    unread_state: Mapped[str] = mapped_column(String(16), nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(16), nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(16), nullable=False)

    data_series: Mapped["DataSeries"] = relationship(
        back_populates="user_trend_notifications"
    )
    event: Mapped["TrendChangeEvent"] = relationship(back_populates="notifications")
    user: Mapped["UserAccount"] = relationship(back_populates="trend_notifications")
