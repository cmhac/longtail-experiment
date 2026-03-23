"""Topic tag models for dataset-level metadata discovery."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .data_series import DataSeries


class DataSeriesTopicTag(Base):
    """Association table joining data series and topic tags."""

    __tablename__ = "data_series_topic_tags"

    data_series_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("data_series.id", ondelete="CASCADE"),
        primary_key=True,
    )
    topic_tag_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topic_tags.id", ondelete="CASCADE"),
        primary_key=True,
    )


class TopicTag(Base):
    """Human-readable topic tag that can be linked to many datasets."""

    __tablename__ = "topic_tags"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    tag_name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    data_series: Mapped[list["DataSeries"]] = relationship(
        secondary="data_series_topic_tags", back_populates="topic_tags"
    )
