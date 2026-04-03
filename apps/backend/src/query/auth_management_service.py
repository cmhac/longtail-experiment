"""Auth/account orchestration service for backend request handlers."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal, Protocol, cast

from src.contract.errors import ContractQueryError
from src.contract.query.auth_management_query import (
    AdminUserListResponse,
    AdminUserSummary,
    AuthSessionResponse,
    CurrentUserSummary,
    SessionListResponse,
    SessionSummary,
)

from .auth_management_validators import (
    ensure_account_active,
    normalize_display_name,
    normalize_email,
    parse_lockout_until,
    validate_password_strength,
)


class AuthServiceRepository(Protocol):
    """Repository contract consumed by auth/account service workflows."""

    def create_user_account(
        self,
        *,
        email: str,
        password_hash: str,
        display_name: str | None,
        is_admin: bool,
    ) -> dict[str, object]:
        """Create a new user account and primary credential record."""
        ...

    def get_user_by_email(self, *, email: str) -> dict[str, object] | None:
        """Fetch a user by normalized email address."""
        ...

    def get_user_by_id(self, *, user_id: str) -> dict[str, object] | None:
        """Fetch a user by canonical user identifier."""
        ...

    def update_failed_sign_in(
        self,
        *,
        user_id: str,
        failed_sign_in_count: int,
        lockout_until: str | None,
    ) -> None:
        """Persist failed sign-in counters and optional lockout timestamp."""
        ...

    def update_password_hash(self, *, user_id: str, password_hash: str) -> None:
        """Rotate the active password hash for a user account."""
        ...

    def create_session(
        self,
        *,
        user_id: str,
        expires_at: str,
        client_metadata: dict[str, object] | None,
    ) -> dict[str, object]:
        """Create a new active auth session for the user."""
        ...

    def get_active_session(self, *, session_id: str) -> dict[str, object] | None:
        """Load an active session with the associated user projection."""
        ...

    def list_active_sessions(self, *, user_id: str) -> list[dict[str, object]]:
        """List active sessions for a user ordered by recency."""
        ...

    def revoke_session(self, *, user_id: str, session_id: str, reason: str) -> bool:
        """Revoke a single active session and return whether it existed."""
        ...

    def revoke_all_sessions_for_user(self, *, user_id: str, reason: str) -> int:
        """Revoke every active session for a user and return affected rows."""
        ...

    def list_admin_users(self) -> list[dict[str, object]]:
        """List user projections used by admin account-management screens."""
        ...

    def write_audit_event(
        self,
        *,
        event_type: str,
        user_id: str | None,
        actor_user_id: str | None,
        event_context: dict[str, object] | None,
    ) -> None:
        """Persist an account-audit event for auth lifecycle actions."""
        ...


@dataclass(slots=True)
class AuthManagementService:
    """Coordinate auth/account workflows across validation and persistence."""

    repository: AuthServiceRepository
    session_ttl: timedelta = timedelta(days=30)
    lockout_threshold: int = 5
    lockout_window: timedelta = timedelta(minutes=15)

    def register_account(
        self,
        *,
        email: str,
        password: str,
        display_name: str | None,
        client_metadata: dict[str, object] | None = None,
    ) -> AuthSessionResponse:
        """Register a new account and immediately return an active session."""
        normalized_email = normalize_email(email)
        validate_password_strength(password)
        normalized_display_name = normalize_display_name(display_name)

        existing = self.repository.get_user_by_email(email=normalized_email)
        if existing is not None:
            raise ContractQueryError("duplicate_email")

        account = self.repository.create_user_account(
            email=normalized_email,
            password_hash=self._hash_password(password),
            display_name=normalized_display_name,
            is_admin=False,
        )
        self.repository.write_audit_event(
            event_type="register",
            user_id=str(account["user_id"]),
            actor_user_id=str(account["user_id"]),
            event_context={"email": normalized_email},
        )
        return self._create_session_response(
            user_id=str(account["user_id"]),
            client_metadata=client_metadata,
        )

    def login(
        self,
        *,
        email: str,
        password: str,
        client_metadata: dict[str, object] | None = None,
    ) -> AuthSessionResponse:
        """Authenticate credentials and return a newly created active session."""
        normalized_email = normalize_email(email)
        account = self.repository.get_user_by_email(email=normalized_email)
        if account is None:
            raise ContractQueryError("invalid_credentials")

        ensure_account_active(str(account["account_status"]))
        lockout_until = parse_lockout_until(account.get("lockout_until"))
        now = datetime.now(tz=UTC)
        if lockout_until is not None and lockout_until > now:
            raise ContractQueryError("account_locked")

        if not self._verify_password(password, str(account.get("password_hash") or "")):
            failed_sign_in_raw = account.get("failed_sign_in_count")
            failed_sign_in_count = (
                int(failed_sign_in_raw) + 1 if isinstance(failed_sign_in_raw, int | str) else 1
            )
            lockout_expires = (
                now + self.lockout_window
                if failed_sign_in_count >= self.lockout_threshold
                else None
            )
            self.repository.update_failed_sign_in(
                user_id=str(account["user_id"]),
                failed_sign_in_count=failed_sign_in_count,
                lockout_until=lockout_expires.isoformat() if lockout_expires else None,
            )
            self.repository.write_audit_event(
                event_type=("lockout_applied" if lockout_expires else "sign_in_failure"),
                user_id=str(account["user_id"]),
                actor_user_id=str(account["user_id"]),
                event_context={"failed_sign_in_count": failed_sign_in_count},
            )
            raise ContractQueryError("invalid_credentials")

        self.repository.update_failed_sign_in(
            user_id=str(account["user_id"]),
            failed_sign_in_count=0,
            lockout_until=None,
        )
        self.repository.write_audit_event(
            event_type="sign_in_success",
            user_id=str(account["user_id"]),
            actor_user_id=str(account["user_id"]),
            event_context=None,
        )
        return self._create_session_response(
            user_id=str(account["user_id"]),
            client_metadata=client_metadata,
        )

    def authenticate_session(self, *, session_id: str) -> dict[str, object]:
        """Validate a session token and return hydrated user/session context."""
        session = self.repository.get_active_session(session_id=session_id)
        if session is None:
            raise ContractQueryError("auth_required")

        user = session.get("user")
        if not isinstance(user, dict):
            raise ContractQueryError("auth_required")

        typed_user = cast(dict[str, object], user)
        ensure_account_active(str(typed_user.get("account_status") or ""))
        return session

    def logout(self, *, user_id: str, session_id: str) -> None:
        """Revoke a single session during user sign-out."""
        revoked = self.repository.revoke_session(
            user_id=user_id,
            session_id=session_id,
            reason="sign_out",
        )
        if not revoked:
            raise ContractQueryError("session_not_found")
        self.repository.write_audit_event(
            event_type="sign_out",
            user_id=user_id,
            actor_user_id=user_id,
            event_context={"session_id": session_id},
        )

    def list_user_sessions(self, *, user_id: str) -> SessionListResponse:
        """Return all active sessions owned by the specified user."""
        sessions = [
            SessionSummary.model_validate(item)
            for item in self.repository.list_active_sessions(user_id=user_id)
        ]
        return SessionListResponse(items=sessions)

    def revoke_user_session(self, *, user_id: str, session_id: str) -> None:
        """Revoke one of the user's active sessions."""
        revoked = self.repository.revoke_session(
            user_id=user_id,
            session_id=session_id,
            reason="user_revoke",
        )
        if not revoked:
            raise ContractQueryError("session_not_found")
        self.repository.write_audit_event(
            event_type="session_revoked",
            user_id=user_id,
            actor_user_id=user_id,
            event_context={"session_id": session_id},
        )

    def list_admin_users(self) -> AdminUserListResponse:
        """Return the admin-facing list of user account summaries."""
        users = [
            AdminUserSummary.model_validate(item) for item in self.repository.list_admin_users()
        ]
        return AdminUserListResponse(items=users)

    def _create_session_response(
        self,
        *,
        user_id: str,
        client_metadata: dict[str, object] | None,
    ) -> AuthSessionResponse:
        account = self.repository.get_user_by_id(user_id=user_id)
        if account is None:
            raise ContractQueryError("account_not_found")

        now = datetime.now(tz=UTC)
        session_payload = self.repository.create_session(
            user_id=user_id,
            expires_at=(now + self.session_ttl).isoformat(),
            client_metadata=client_metadata,
        )

        return AuthSessionResponse(
            user=CurrentUserSummary(
                user_id=user_id,
                email=str(account["email"]),
                display_name=(
                    str(account["display_name"])
                    if account.get("display_name") is not None
                    else None
                ),
                account_status=cast(
                    Literal["active", "deactivated", "deletion_pending", "deleted"],
                    str(account["account_status"]),
                ),
                is_admin=bool(account.get("is_admin") or False),
            ),
            session=SessionSummary.model_validate(session_payload),
        )

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @classmethod
    def _verify_password(cls, password: str, persisted_hash: str) -> bool:
        return cls._hash_password(password) == persisted_hash
