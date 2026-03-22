"""Runtime ingestion state models for orchestration and auditability."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class SourceRunLock(Base):
    """Per-source lock table enforcing one active and one queued trigger."""

    __tablename__ = "source_run_locks"

    source_key: Mapped[str] = mapped_column(String(255), primary_key=True)
    active_run_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    queued_trigger_token: Mapped[str | None] = mapped_column(String(64), nullable=True)
    lock_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class IngestionRun(Base):
    """Aggregate run-level lifecycle and outcome counters."""

    __tablename__ = "ingestion_runs"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    run_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(32), nullable=False)
    lifecycle_state: Mapped[str] = mapped_column(String(32), nullable=False)
    outcome_state: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    accepted_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quarantined_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicate_no_op_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    conflict_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    due_source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    executed_source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    deferred_source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    not_due_source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class SourceSchedulePolicy(Base):
    """Persisted schedule-policy state for one registered source."""

    __tablename__ = "source_schedule_policies"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    source_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    cadence_type: Mapped[str] = mapped_column(String(32), nullable=False)
    cadence_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="UTC")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_successful_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_eligible_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    priority_class: Mapped[str] = mapped_column(String(32), nullable=False, default="normal")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SourceEligibilitySnapshot(Base):
    """Per-source due-state decision persisted for one run."""

    __tablename__ = "source_eligibility_snapshots"
    __table_args__ = (
        UniqueConstraint("run_id", "source_key", name="uq_eligibility_run_source"),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    run_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("ingestion_runs.run_id"), nullable=False
    )
    source_key: Mapped[str] = mapped_column(String(255), nullable=False)
    eligibility_state: Mapped[str] = mapped_column(String(32), nullable=False)
    reason_code: Mapped[str] = mapped_column(String(64), nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    selected_for_execution: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class SourceRunOutcome(Base):
    """Source-scoped outcomes for one run."""

    __tablename__ = "source_run_outcomes"
    __table_args__ = (
        UniqueConstraint("run_id", "source_key", name="uq_outcome_run_source"),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    run_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("ingestion_runs.run_id"), nullable=False
    )
    source_key: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    accepted_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quarantined_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicate_no_op_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    conflict_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    outcome_reason_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)


class ConflictRecord(Base):
    """Persisted conflict record for duplicate drift mismatches."""

    __tablename__ = "conflict_records"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    conflict_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    run_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("ingestion_runs.run_id"), nullable=False
    )
    source_key: Mapped[str] = mapped_column(String(255), nullable=False)
    series_key: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_period_key: Mapped[str] = mapped_column(String(64), nullable=False)
    existing_observation_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    incoming_record_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    conflict_type: Mapped[str] = mapped_column(String(64), nullable=False)
    conflict_state: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
