"""Add privilege level and owner role governance support.

Revision ID: 0014_owner_privilege_governance
Revises: 0013_user_auth_management
Create Date: 2026-04-03
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0014_owner_privilege_governance"
down_revision: str | None = "0013_user_auth_management"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Introduce explicit privilege level with owner constraints."""

    op.add_column(
        "user_accounts",
        sa.Column(
            "privilege_level",
            sa.String(length=16),
            nullable=False,
            server_default="user",
        ),
    )
    op.create_check_constraint(
        "ck_user_accounts_privilege_level",
        "user_accounts",
        "privilege_level IN ('user', 'admin', 'owner')",
    )

    op.execute(
        """
        UPDATE user_accounts
        SET privilege_level = 'admin'
        WHERE EXISTS (
            SELECT 1
            FROM role_assignments ra
            WHERE ra.user_id = user_accounts.id
              AND ra.role = 'admin'
              AND ra.revoked_at IS NULL
        )
        """
    )

    op.alter_column("user_accounts", "privilege_level", server_default=None)

    op.drop_constraint(
        "ck_account_audit_events_type",
        "account_audit_events",
        type_="check",
    )
    op.create_check_constraint(
        "ck_account_audit_events_type",
        "account_audit_events",
        "event_type IN ("
        "'register', 'sign_in_success', 'sign_in_failure', 'lockout_applied', "
        "'sign_out', 'password_changed', 'session_revoked', 'account_deactivated', "
        "'account_reactivated', 'deletion_requested', 'account_hard_deleted', "
        "'admin_granted', 'admin_revoked', 'admin_role_update_denied'"
        ")",
    )


def downgrade() -> None:
    """Remove explicit privilege level governance column."""

    op.drop_constraint(
        "ck_user_accounts_privilege_level",
        "user_accounts",
        type_="check",
    )
    op.drop_column("user_accounts", "privilege_level")

    op.drop_constraint(
        "ck_account_audit_events_type",
        "account_audit_events",
        type_="check",
    )
    op.create_check_constraint(
        "ck_account_audit_events_type",
        "account_audit_events",
        "event_type IN ("
        "'register', 'sign_in_success', 'sign_in_failure', 'lockout_applied', "
        "'sign_out', 'password_changed', 'session_revoked', 'account_deactivated', "
        "'account_reactivated', 'deletion_requested', 'account_hard_deleted'"
        ")",
    )
