"""Auth/account persistence models used by backend and frontend workflows."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserAccount(Base):
    """Persist one user identity with account lifecycle metadata."""

    __tablename__ = "user_accounts"
    __table_args__ = (
        CheckConstraint(
            "account_status IN ('active', 'deactivated', 'deletion_pending', 'deleted')",
            name="ck_user_accounts_status",
        ),
        CheckConstraint(
            "privilege_level IN ('user', 'admin', 'owner')",
            name="ck_user_accounts_privilege_level",
        ),
        CheckConstraint(
            "deletion_due_at IS NULL OR deletion_requested_at IS NOT NULL",
            name="ck_user_accounts_deletion_due_requires_request",
        ),
        Index("ix_user_accounts_email_normalized", "email_normalized", unique=True),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    email_normalized: Mapped[str] = mapped_column(String(320), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    account_status: Mapped[str] = mapped_column(String(32), nullable=False)
    privilege_level: Mapped[str] = mapped_column(
        String(16), nullable=False, default="user"
    )
    failed_sign_in_count: Mapped[int] = mapped_column(default=0, nullable=False)
    lockout_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    deactivated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deletion_requested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deletion_due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    credentials: Mapped[list["CredentialRecord"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions: Mapped[list["AuthSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    role_assignments: Mapped[list["RoleAssignment"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class CredentialRecord(Base):
    """Persist password-hash lifecycle metadata for one account."""

    __tablename__ = "credential_records"
    __table_args__ = (
        CheckConstraint(
            "credential_status IN ('active', 'rotated', 'revoked')",
            name="ck_credential_records_status",
        ),
        UniqueConstraint(
            "user_id",
            "credential_status",
            name="uq_credential_records_user_status",
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
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    password_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    credential_status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    user: Mapped[UserAccount] = relationship(back_populates="credentials")


class AuthSession(Base):
    """Persist one authenticated user session with revocation state."""

    __tablename__ = "auth_sessions"
    __table_args__ = (
        CheckConstraint(
            "session_status IN ('active', 'revoked', 'expired')",
            name="ck_auth_sessions_status",
        ),
        Index("ix_auth_sessions_user_id_status", "user_id", "session_status"),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_status: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    client_metadata: Mapped[dict[str, object] | None] = mapped_column(
        JSONB, nullable=True
    )

    user: Mapped[UserAccount] = relationship(back_populates="sessions")


class RoleAssignment(Base):
    """Persist role grants for administrative authorization checks."""

    __tablename__ = "role_assignments"
    __table_args__ = (
        CheckConstraint("role IN ('admin')", name="ck_role_assignments_role"),
        Index("ix_role_assignments_user_id_revoked", "user_id", "revoked_at"),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped[UserAccount] = relationship(back_populates="role_assignments")


class AccountAuditEvent(Base):
    """Persist immutable account and session security events."""

    __tablename__ = "account_audit_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ("
            "'register', 'sign_in_success', 'sign_in_failure', 'lockout_applied', "
            "'sign_out', 'password_changed', 'session_revoked', 'account_deactivated', "
            "'account_reactivated', 'deletion_requested', 'account_hard_deleted', "
            "'admin_granted', 'admin_revoked', 'admin_role_update_denied'"
            ")",
            name="ck_account_audit_events_type",
        ),
        Index("ix_account_audit_events_occurred_at", "occurred_at"),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    actor_user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    event_context: Mapped[dict[str, object] | None] = mapped_column(
        JSONB, nullable=True
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


__all__ = [
    "AccountAuditEvent",
    "AuthSession",
    "CredentialRecord",
    "RoleAssignment",
    "UserAccount",
]
