"""Add user account, credential, session, role, and audit-event tables.

Revision ID: 0013_user_auth_management
Revises: 0012_lookback_trend_snapshots
Create Date: 2026-04-02
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0013_user_auth_management"
down_revision: str | None = "0012_lookback_trend_snapshots"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create shared auth/account foundation tables."""

    op.create_table(
        "user_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("email_normalized", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("account_status", sa.String(length=32), nullable=False),
        sa.Column(
            "failed_sign_in_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("lockout_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deletion_requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deletion_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "account_status IN ('active', 'deactivated', 'deletion_pending', 'deleted')",
            name="ck_user_accounts_status",
        ),
        sa.CheckConstraint(
            "deletion_due_at IS NULL OR deletion_requested_at IS NOT NULL",
            name="ck_user_accounts_deletion_due_requires_request",
        ),
    )
    op.create_index(
        "ix_user_accounts_email_normalized",
        "user_accounts",
        ["email_normalized"],
        unique=True,
    )

    op.create_table(
        "credential_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("credential_status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "credential_status",
            name="uq_credential_records_user_status",
        ),
        sa.CheckConstraint(
            "credential_status IN ('active', 'rotated', 'revoked')",
            name="ck_credential_records_status",
        ),
    )

    op.create_table(
        "auth_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_reason", sa.String(length=255), nullable=True),
        sa.Column("client_metadata", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "session_status IN ('active', 'revoked', 'expired')",
            name="ck_auth_sessions_status",
        ),
    )
    op.create_index(
        "ix_auth_sessions_user_id_status",
        "auth_sessions",
        ["user_id", "session_status"],
        unique=False,
    )

    op.create_table(
        "role_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("role IN ('admin')", name="ck_role_assignments_role"),
    )
    op.create_index(
        "ix_role_assignments_user_id_revoked",
        "role_assignments",
        ["user_id", "revoked_at"],
        unique=False,
    )

    op.create_table(
        "account_audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("event_context", postgresql.JSONB(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["actor_user_id"], ["user_accounts.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "event_type IN ("
            "'register', 'sign_in_success', 'sign_in_failure', 'lockout_applied', "
            "'sign_out', 'password_changed', 'session_revoked', 'account_deactivated', "
            "'account_reactivated', 'deletion_requested', 'account_hard_deleted'"
            ")",
            name="ck_account_audit_events_type",
        ),
    )
    op.create_index(
        "ix_account_audit_events_occurred_at",
        "account_audit_events",
        ["occurred_at"],
        unique=False,
    )


def downgrade() -> None:
    """Drop shared auth/account foundation tables."""

    op.drop_index(
        "ix_account_audit_events_occurred_at", table_name="account_audit_events"
    )
    op.drop_table("account_audit_events")
    op.drop_index("ix_role_assignments_user_id_revoked", table_name="role_assignments")
    op.drop_table("role_assignments")
    op.drop_index("ix_auth_sessions_user_id_status", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_table("credential_records")
    op.drop_index("ix_user_accounts_email_normalized", table_name="user_accounts")
    op.drop_table("user_accounts")
