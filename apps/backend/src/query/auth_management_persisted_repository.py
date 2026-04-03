"""Backend persisted repository adapter for auth/account service workflows."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Engine, text

from src.contract.errors import ContractQueryError


def _iso_datetime(value: datetime) -> str:
    return value.astimezone(UTC).isoformat()


class PersistedAuthManagementRepository:
    """Read and write auth/account records from PostgreSQL runtime storage."""

    def __init__(self, *, engine: Engine) -> None:
        """Bind the SQLAlchemy engine used for auth/account persistence calls."""
        self._engine = engine

    def create_user_account(
        self,
        *,
        email: str,
        password_hash: str,
        display_name: str | None,
        is_admin: bool,
    ) -> dict[str, object]:
        """Insert user, credential, and optional admin role records."""
        now = datetime.now(tz=UTC)
        user_id = uuid4()
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO user_accounts (
                        id,
                        email,
                        email_normalized,
                        display_name,
                        account_status,
                        privilege_level,
                        failed_sign_in_count,
                        lockout_until,
                        created_at,
                        updated_at,
                        deactivated_at,
                        deletion_requested_at,
                        deletion_due_at,
                        deleted_at
                    ) VALUES (
                        :id,
                        :email,
                        :email_normalized,
                        :display_name,
                        'active',
                        :privilege_level,
                        0,
                        NULL,
                        :created_at,
                        :updated_at,
                        NULL,
                        NULL,
                        NULL,
                        NULL
                    )
                    """
                ),
                {
                    "id": user_id,
                    "email": email,
                    "email_normalized": email.strip().lower(),
                    "display_name": display_name,
                    "privilege_level": "admin" if is_admin else "user",
                    "created_at": now,
                    "updated_at": now,
                },
            )
            connection.execute(
                text(
                    """
                    INSERT INTO credential_records (
                        id,
                        user_id,
                        password_hash,
                        password_changed_at,
                        credential_status,
                        created_at,
                        updated_at
                    ) VALUES (
                        :id,
                        :user_id,
                        :password_hash,
                        :password_changed_at,
                        'active',
                        :created_at,
                        :updated_at
                    )
                    """
                ),
                {
                    "id": uuid4(),
                    "user_id": user_id,
                    "password_hash": password_hash,
                    "password_changed_at": now,
                    "created_at": now,
                    "updated_at": now,
                },
            )
            if is_admin:
                connection.execute(
                    text(
                        """
                        INSERT INTO role_assignments (
                            id,
                            user_id,
                            role,
                            created_at,
                            revoked_at
                        ) VALUES (
                            :id,
                            :user_id,
                            'admin',
                            :created_at,
                            NULL
                        )
                        """
                    ),
                    {
                        "id": uuid4(),
                        "user_id": user_id,
                        "created_at": now,
                    },
                )
        return self.get_user_by_id(user_id=str(user_id)) or {}

    def get_user_by_email(self, *, email: str) -> dict[str, object] | None:
        """Fetch a single user projection by normalized email."""
        with self._engine.begin() as connection:
            row = (
                connection.execute(
                    text(
                        """
                        SELECT
                            ua.id,
                            ua.email,
                            ua.email_normalized,
                            ua.display_name,
                            ua.account_status,
                            ua.privilege_level,
                            ua.failed_sign_in_count,
                            ua.lockout_until,
                            ua.updated_at,
                            cr.password_hash,
                            EXISTS (
                                SELECT 1
                                FROM role_assignments ra
                                WHERE ra.user_id = ua.id
                                  AND ra.role = 'admin'
                                  AND ra.revoked_at IS NULL
                            ) AS is_admin
                        FROM user_accounts ua
                        LEFT JOIN credential_records cr
                            ON cr.user_id = ua.id
                           AND cr.credential_status = 'active'
                        WHERE ua.email_normalized = :email_normalized
                        LIMIT 1
                        """
                    ),
                    {"email_normalized": email.strip().lower()},
                )
                .mappings()
                .first()
            )
        if row is None:
            return None
        return self._serialize_user_row(dict(row))

    def get_user_by_id(self, *, user_id: str) -> dict[str, object] | None:
        """Fetch a single user projection by user identifier."""
        with self._engine.begin() as connection:
            row = (
                connection.execute(
                    text(
                        """
                        SELECT
                            ua.id,
                            ua.email,
                            ua.email_normalized,
                            ua.display_name,
                            ua.account_status,
                            ua.privilege_level,
                            ua.failed_sign_in_count,
                            ua.lockout_until,
                            ua.updated_at,
                            cr.password_hash,
                            EXISTS (
                                SELECT 1
                                FROM role_assignments ra
                                WHERE ra.user_id = ua.id
                                  AND ra.role = 'admin'
                                  AND ra.revoked_at IS NULL
                            ) AS is_admin
                        FROM user_accounts ua
                        LEFT JOIN credential_records cr
                            ON cr.user_id = ua.id
                           AND cr.credential_status = 'active'
                        WHERE ua.id = :user_id
                        LIMIT 1
                        """
                    ),
                    {"user_id": UUID(user_id)},
                )
                .mappings()
                .first()
            )
        if row is None:
            return None
        return self._serialize_user_row(dict(row))

    def update_failed_sign_in(
        self,
        *,
        user_id: str,
        failed_sign_in_count: int,
        lockout_until: str | None,
    ) -> None:
        """Persist failed sign-in counters and lockout timestamp."""
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE user_accounts
                    SET
                        failed_sign_in_count = :failed_sign_in_count,
                        lockout_until = :lockout_until,
                        updated_at = :updated_at
                    WHERE id = :user_id
                    """
                ),
                {
                    "failed_sign_in_count": failed_sign_in_count,
                    "lockout_until": (
                        datetime.fromisoformat(lockout_until) if lockout_until is not None else None
                    ),
                    "updated_at": datetime.now(tz=UTC),
                    "user_id": UUID(user_id),
                },
            )

    def update_password_hash(self, *, user_id: str, password_hash: str) -> None:
        """Update active credential hash and password-changed timestamp."""
        now = datetime.now(tz=UTC)
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE credential_records
                    SET
                        password_hash = :password_hash,
                        password_changed_at = :password_changed_at,
                        updated_at = :updated_at
                    WHERE user_id = :user_id
                      AND credential_status = 'active'
                    """
                ),
                {
                    "password_hash": password_hash,
                    "password_changed_at": now,
                    "updated_at": now,
                    "user_id": UUID(user_id),
                },
            )

    def update_user_profile(
        self,
        *,
        user_id: str,
        email: str | None,
        display_name: str | None,
    ) -> dict[str, object] | None:
        """Update one user's display name and return the latest projection."""
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE user_accounts
                    SET
                        email = COALESCE(:email, email),
                        email_normalized = COALESCE(:email_normalized, email_normalized),
                        display_name = :display_name,
                        updated_at = :updated_at
                    WHERE id = :user_id
                    """
                ),
                {
                    "email": email,
                    "email_normalized": (email.strip().lower() if email is not None else None),
                    "display_name": display_name,
                    "updated_at": datetime.now(tz=UTC),
                    "user_id": UUID(user_id),
                },
            )
        return self.get_user_by_id(user_id=user_id)

    def change_password_and_revoke_sessions(
        self,
        *,
        user_id: str,
        password_hash: str,
        reason: str,
    ) -> int:
        """Rotate password hash and revoke all active sessions in one transaction."""
        now = datetime.now(tz=UTC)
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE credential_records
                    SET
                        password_hash = :password_hash,
                        password_changed_at = :password_changed_at,
                        updated_at = :updated_at
                    WHERE user_id = :user_id
                      AND credential_status = 'active'
                    """
                ),
                {
                    "password_hash": password_hash,
                    "password_changed_at": now,
                    "updated_at": now,
                    "user_id": UUID(user_id),
                },
            )
            rows = connection.execute(
                text(
                    """
                    UPDATE auth_sessions
                    SET
                        session_status = 'revoked',
                        revoked_at = :revoked_at,
                        revoked_reason = :revoked_reason
                    WHERE user_id = :user_id
                      AND session_status = 'active'
                    """
                ),
                {
                    "revoked_at": now,
                    "revoked_reason": reason,
                    "user_id": UUID(user_id),
                },
            )
        return int(rows.rowcount or 0)

    def request_account_deletion(
        self,
        *,
        user_id: str,
        deletion_due_at: str,
    ) -> dict[str, object] | None:
        """Transition account to deletion_pending and return updated projection."""
        now = datetime.now(tz=UTC)
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE user_accounts
                    SET
                        account_status = CASE
                            WHEN account_status = 'deleted' THEN account_status
                            ELSE 'deletion_pending'
                        END,
                        deactivated_at = COALESCE(deactivated_at, :now),
                        deletion_requested_at = COALESCE(deletion_requested_at, :now),
                        deletion_due_at = COALESCE(
                            deletion_due_at,
                            :deletion_due_at
                        ),
                        updated_at = :now
                    WHERE id = :user_id
                    """
                ),
                {
                    "now": now,
                    "deletion_due_at": datetime.fromisoformat(deletion_due_at),
                    "user_id": UUID(user_id),
                },
            )
        return self.get_user_by_id(user_id=user_id)

    def create_session(
        self,
        *,
        user_id: str,
        expires_at: str,
        client_metadata: dict[str, object] | None,
    ) -> dict[str, object]:
        """Create and return a new active auth session projection."""
        now = datetime.now(tz=UTC)
        session_id = uuid4()
        expires_at_dt = datetime.fromisoformat(expires_at)
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO auth_sessions (
                        id,
                        user_id,
                        session_status,
                        created_at,
                        expires_at,
                        revoked_at,
                        revoked_reason,
                        client_metadata
                    ) VALUES (
                        :id,
                        :user_id,
                        'active',
                        :created_at,
                        :expires_at,
                        NULL,
                        NULL,
                        :client_metadata
                    )
                    """
                ),
                {
                    "id": session_id,
                    "user_id": UUID(user_id),
                    "created_at": now,
                    "expires_at": expires_at_dt,
                    "client_metadata": (
                        json.dumps(client_metadata) if client_metadata is not None else None
                    ),
                },
            )
        return {
            "session_id": str(session_id),
            "created_at": _iso_datetime(now),
            "expires_at": _iso_datetime(expires_at_dt),
            "session_status": "active",
            "client_label": (
                str(client_metadata.get("client_label"))
                if isinstance(client_metadata, dict)
                and isinstance(client_metadata.get("client_label"), str)
                else None
            ),
        }

    def get_active_session(self, *, session_id: str) -> dict[str, object] | None:
        """Return active session details with embedded current-user payload."""
        now = datetime.now(tz=UTC)
        with self._engine.begin() as connection:
            row = (
                connection.execute(
                    text(
                        """
                        SELECT
                            s.id,
                            s.user_id,
                            s.session_status,
                            s.created_at,
                            s.expires_at,
                            s.client_metadata,
                            ua.email,
                            ua.display_name,
                            ua.account_status,
                            ua.privilege_level,
                            EXISTS (
                                SELECT 1
                                FROM role_assignments ra
                                WHERE ra.user_id = ua.id
                                  AND ra.role = 'admin'
                                  AND ra.revoked_at IS NULL
                            ) AS is_admin
                        FROM auth_sessions s
                        JOIN user_accounts ua ON ua.id = s.user_id
                        WHERE s.id = :session_id
                          AND s.session_status = 'active'
                          AND s.expires_at > :now
                        LIMIT 1
                        """
                    ),
                    {
                        "session_id": UUID(session_id),
                        "now": now,
                    },
                )
                .mappings()
                .first()
            )
        if row is None:
            return None
        return {
            "session_id": str(row["id"]),
            "user_id": str(row["user_id"]),
            "created_at": _iso_datetime(row["created_at"]),
            "expires_at": _iso_datetime(row["expires_at"]),
            "session_status": str(row["session_status"]),
            "client_metadata": (
                row["client_metadata"]
                if isinstance(row["client_metadata"], dict)
                else (
                    json.loads(row["client_metadata"])
                    if isinstance(row["client_metadata"], str)
                    else None
                )
            ),
            "user": {
                "user_id": str(row["user_id"]),
                "email": str(row["email"]),
                "display_name": row["display_name"],
                "account_status": str(row["account_status"]),
                "is_admin": bool(
                    row["is_admin"] or str(row["privilege_level"]) in {"admin", "owner"}
                ),
                "privilege_level": str(row["privilege_level"]),
            },
        }

    def list_active_sessions(self, *, user_id: str) -> list[dict[str, object]]:
        """List active sessions for a user in descending created order."""
        with self._engine.begin() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT
                        id,
                        created_at,
                        expires_at,
                        session_status,
                        client_metadata
                    FROM auth_sessions
                    WHERE user_id = :user_id
                      AND session_status = 'active'
                    ORDER BY created_at DESC
                    """
                ),
                {"user_id": UUID(user_id)},
            ).mappings()
            result = rows.all()
        return [
            {
                "session_id": str(row["id"]),
                "created_at": _iso_datetime(row["created_at"]),
                "expires_at": _iso_datetime(row["expires_at"]),
                "session_status": str(row["session_status"]),
                "client_label": (
                    str(row["client_metadata"].get("client_label"))
                    if isinstance(row["client_metadata"], dict)
                    and isinstance(row["client_metadata"].get("client_label"), str)
                    else None
                ),
            }
            for row in result
        ]

    def revoke_session(self, *, user_id: str, session_id: str, reason: str) -> bool:
        """Revoke one active session and report whether a row was changed."""
        with self._engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    UPDATE auth_sessions
                    SET
                        session_status = 'revoked',
                        revoked_at = :revoked_at,
                        revoked_reason = :revoked_reason
                    WHERE id = :session_id
                      AND user_id = :user_id
                      AND session_status = 'active'
                    RETURNING id
                    """
                ),
                {
                    "revoked_at": datetime.now(tz=UTC),
                    "revoked_reason": reason,
                    "session_id": UUID(session_id),
                    "user_id": UUID(user_id),
                },
            ).scalar_one_or_none()
        return row is not None

    def revoke_all_sessions_for_user(self, *, user_id: str, reason: str) -> int:
        """Revoke every active session for the user and return row count."""
        with self._engine.begin() as connection:
            rows = connection.execute(
                text(
                    """
                    UPDATE auth_sessions
                    SET
                        session_status = 'revoked',
                        revoked_at = :revoked_at,
                        revoked_reason = :revoked_reason
                    WHERE user_id = :user_id
                      AND session_status = 'active'
                    """
                ),
                {
                    "revoked_at": datetime.now(tz=UTC),
                    "revoked_reason": reason,
                    "user_id": UUID(user_id),
                },
            )
        return int(rows.rowcount or 0)

    def list_admin_users(self) -> list[dict[str, object]]:
        """List account summaries consumed by admin management endpoints."""
        with self._engine.begin() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT
                        ua.id,
                        ua.email,
                        ua.display_name,
                        ua.account_status,
                        ua.privilege_level,
                        ua.updated_at,
                        EXISTS (
                            SELECT 1
                            FROM role_assignments ra
                            WHERE ra.user_id = ua.id
                              AND ra.role = 'admin'
                              AND ra.revoked_at IS NULL
                        ) AS is_admin
                    FROM user_accounts ua
                    ORDER BY ua.created_at DESC
                    """
                )
            ).mappings()
            result = rows.all()
        return [
            {
                "user_id": str(row["id"]),
                "email": str(row["email"]),
                "display_name": row["display_name"],
                "account_status": str(row["account_status"]),
                "is_admin": bool(
                    row["is_admin"] or str(row["privilege_level"]) in {"admin", "owner"}
                ),
                "privilege_level": str(row["privilege_level"]),
                "updated_at": _iso_datetime(row["updated_at"]),
            }
            for row in result
        ]

    def update_admin_user_status(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        account_status: str,
    ) -> tuple[dict[str, object] | None, int]:
        """Update user status with final-admin guard and optional session revocation."""
        now = datetime.now(tz=UTC)
        revoked_count = 0
        with self._engine.begin() as connection:
            target = (
                connection.execute(
                    text(
                        """
                        SELECT
                            ua.id,
                            ua.account_status,
                            EXISTS (
                                SELECT 1
                                FROM role_assignments ra
                                WHERE ra.user_id = ua.id
                                  AND ra.role = 'admin'
                                  AND ra.revoked_at IS NULL
                            ) AS is_admin
                        FROM user_accounts ua
                        WHERE ua.id = :user_id
                        LIMIT 1
                        """
                    ),
                    {"user_id": UUID(user_id)},
                )
                .mappings()
                .first()
            )
            if target is None:
                return None, revoked_count

            if (
                account_status == "deactivated"
                and bool(target["is_admin"])
                and str(target["account_status"]) == "active"
            ):
                remaining_admins = int(
                    connection.execute(
                        text(
                            """
                            SELECT COUNT(*)
                            FROM user_accounts ua
                            WHERE ua.account_status = 'active'
                              AND ua.id <> :user_id
                              AND EXISTS (
                                  SELECT 1
                                  FROM role_assignments ra
                                  WHERE ra.user_id = ua.id
                                    AND ra.role = 'admin'
                                    AND ra.revoked_at IS NULL
                              )
                            """
                        ),
                        {"user_id": UUID(user_id)},
                    ).scalar_one()
                    or 0
                )
                if remaining_admins <= 0:
                    raise ContractQueryError("final_admin_guard")

            connection.execute(
                text(
                    """
                    UPDATE user_accounts
                    SET
                        account_status = CAST(:account_status AS VARCHAR),
                        deactivated_at = CASE
                            WHEN CAST(:account_status AS VARCHAR) = 'deactivated'
                                THEN COALESCE(deactivated_at, :now)
                            ELSE NULL
                        END,
                        updated_at = :now
                    WHERE id = :user_id
                    """
                ),
                {
                    "account_status": account_status,
                    "now": now,
                    "user_id": UUID(user_id),
                },
            )

            if account_status == "deactivated":
                revoked_rows = connection.execute(
                    text(
                        """
                        UPDATE auth_sessions
                        SET
                            session_status = 'revoked',
                            revoked_at = :revoked_at,
                            revoked_reason = :revoked_reason
                        WHERE user_id = :user_id
                          AND session_status = 'active'
                        """
                    ),
                    {
                        "revoked_at": now,
                        "revoked_reason": f"admin_deactivated:{actor_user_id}",
                        "user_id": UUID(user_id),
                    },
                )
                revoked_count = int(revoked_rows.rowcount or 0)

        return self.get_user_by_id(user_id=user_id), revoked_count

    def update_admin_user_role(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        role_action: str,
    ) -> dict[str, object] | None:
        """Grant/revoke admin role with owner-protection guardrails."""
        now = datetime.now(tz=UTC)
        with self._engine.begin() as connection:
            target = (
                connection.execute(
                    text(
                        """
                        SELECT id, privilege_level
                        FROM user_accounts
                        WHERE id = :user_id
                        LIMIT 1
                        """
                    ),
                    {"user_id": UUID(user_id)},
                )
                .mappings()
                .first()
            )
            if target is None:
                return None

            if str(target["privilege_level"]) == "owner":
                self.write_audit_event(
                    event_type="admin_role_update_denied",
                    user_id=user_id,
                    actor_user_id=actor_user_id,
                    event_context={
                        "role_action": role_action,
                        "reason": "owner_role_protected",
                    },
                )
                raise ContractQueryError("owner_role_protected")

            if role_action == "grant_admin":
                connection.execute(
                    text(
                        """
                        UPDATE user_accounts
                        SET privilege_level = 'admin',
                            updated_at = :updated_at
                        WHERE id = :user_id
                        """
                    ),
                    {"updated_at": now, "user_id": UUID(user_id)},
                )
                connection.execute(
                    text(
                        """
                        UPDATE role_assignments
                        SET revoked_at = NULL
                        WHERE user_id = :user_id
                          AND role = 'admin'
                        """
                    ),
                    {"user_id": UUID(user_id)},
                )
                connection.execute(
                    text(
                        """
                        INSERT INTO role_assignments (id, user_id, role, created_at, revoked_at)
                        SELECT :id, :user_id, 'admin', :created_at, NULL
                        WHERE NOT EXISTS (
                            SELECT 1 FROM role_assignments
                            WHERE user_id = :user_id AND role = 'admin'
                        )
                        """
                    ),
                    {"id": uuid4(), "user_id": UUID(user_id), "created_at": now},
                )
            elif role_action == "revoke_admin":
                connection.execute(
                    text(
                        """
                        UPDATE user_accounts
                        SET privilege_level = 'user',
                            updated_at = :updated_at
                        WHERE id = :user_id
                        """
                    ),
                    {"updated_at": now, "user_id": UUID(user_id)},
                )
                connection.execute(
                    text(
                        """
                        UPDATE role_assignments
                        SET revoked_at = :revoked_at
                        WHERE user_id = :user_id
                          AND role = 'admin'
                          AND revoked_at IS NULL
                        """
                    ),
                    {"revoked_at": now, "user_id": UUID(user_id)},
                )
            else:
                raise ContractQueryError("role_action must be grant_admin or revoke_admin")

        self.write_audit_event(
            event_type="admin_granted" if role_action == "grant_admin" else "admin_revoked",
            user_id=user_id,
            actor_user_id=actor_user_id,
            event_context={"role_action": role_action},
        )
        return self.get_user_by_id(user_id=user_id)

    def revoke_all_sessions_for_user_as_admin(self, *, user_id: str, reason: str) -> int:
        """Revoke all active sessions for a target user from admin actions."""
        return self.revoke_all_sessions_for_user(user_id=user_id, reason=reason)

    def write_audit_event(
        self,
        *,
        event_type: str,
        user_id: str | None,
        actor_user_id: str | None,
        event_context: dict[str, object] | None,
    ) -> None:
        """Persist an account audit event for auth/account actions."""
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO account_audit_events (
                        id,
                        user_id,
                        actor_user_id,
                        event_type,
                        event_context,
                        occurred_at
                    ) VALUES (
                        :id,
                        :user_id,
                        :actor_user_id,
                        :event_type,
                        :event_context,
                        :occurred_at
                    )
                    """
                ),
                {
                    "id": uuid4(),
                    "user_id": UUID(user_id) if user_id is not None else None,
                    "actor_user_id": (UUID(actor_user_id) if actor_user_id is not None else None),
                    "event_type": event_type,
                    "event_context": (
                        json.dumps(event_context) if event_context is not None else None
                    ),
                    "occurred_at": datetime.now(tz=UTC),
                },
            )

    @staticmethod
    def _serialize_user_row(row: dict[str, object]) -> dict[str, object]:
        lockout_until_value = row["lockout_until"]
        lockout_until = lockout_until_value if isinstance(lockout_until_value, datetime) else None
        updated_at_value = row["updated_at"]
        updated_at = (
            updated_at_value if isinstance(updated_at_value, datetime) else datetime.now(tz=UTC)
        )
        failed_sign_in_value = row["failed_sign_in_count"]
        privilege_level = str(row.get("privilege_level") or "user")
        return {
            "user_id": str(row["id"]),
            "email": str(row["email"]),
            "email_normalized": str(row["email_normalized"]),
            "display_name": row["display_name"],
            "account_status": str(row["account_status"]),
            "failed_sign_in_count": (
                int(failed_sign_in_value) if isinstance(failed_sign_in_value, int | str) else 0
            ),
            "lockout_until": _iso_datetime(lockout_until) if lockout_until else None,
            "password_hash": row["password_hash"],
            "is_admin": bool(row["is_admin"] or privilege_level in {"admin", "owner"}),
            "privilege_level": privilege_level,
            "updated_at": _iso_datetime(updated_at),
        }
