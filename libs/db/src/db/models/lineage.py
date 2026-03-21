"""Provenance and revision lineage models."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ProvenanceRecord(Base):
    """Immutable source metadata attached to an observation."""

    __tablename__ = "provenance_records"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    observation_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("observations.id"), nullable=False
    )
    source_release_id: Mapped[str] = mapped_column(String(128), nullable=False)
    source_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    observation = relationship("Observation", back_populates="provenance_records")


class RevisionRecord(Base):
    """Links a superseded observation to its replacement."""

    __tablename__ = "revision_records"
    __table_args__ = (
        CheckConstraint(
            "superseded_observation_id <> current_observation_id",
            name="ck_revision_distinct_observations",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    superseded_observation_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("observations.id"), nullable=False
    )
    current_observation_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("observations.id"), nullable=False
    )
    reason: Mapped[str] = mapped_column(String(255), nullable=False)

    superseded_observation = relationship(
        "Observation",
        foreign_keys=[superseded_observation_id],
        back_populates="superseded_by",
    )
    current_observation = relationship(
        "Observation",
        foreign_keys=[current_observation_id],
        back_populates="supersedes",
    )
