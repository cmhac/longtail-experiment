"""Auth/account orchestration service for backend request handlers."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal, Protocol, cast

from src.contract.errors import ContractQueryError
from src.contract.query.auth_management_query import (
    AccountNavigationResponse,
    AdminNavigationItem,
    AdminNavigationResponse,
    AdminUserListResponse,
    AdminUserSummary,
    AuthSessionResponse,
    CurrentUserSummary,
    DeletionRequestResponse,
    ProfileResponse,
    SessionListResponse,
    SessionSummary,
)

from .auth_management_validators import (
    ensure_account_active,
    normalize_display_name,
    normalize_email,
    normalize_optional_email,
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

    def update_user_profile(
        self,
        *,
        user_id: str,
        email: str | None,
        display_name: str | None,
    ) -> dict[str, object] | None:
        """Update one user's profile fields and return the latest projection."""
        ...

    def change_password_and_revoke_sessions(
        self,
        *,
        user_id: str,
        password_hash: str,
        reason: str,
    ) -> int:
        """Rotate password hash and revoke all active sessions atomically."""
        ...

    def request_account_deletion(
        self,
        *,
        user_id: str,
        deletion_due_at: str,
    ) -> dict[str, object] | None:
        """Transition account lifecycle to deletion pending and return projection."""
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

    def update_admin_user_status(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        account_status: Literal["active", "deactivated"],
    ) -> tuple[dict[str, object] | None, int]:
        """Update account status and return updated user plus revoked session count."""
        ...

    def revoke_all_sessions_for_user_as_admin(self, *, user_id: str, reason: str) -> int:
        """Revoke every active session for a target user from admin workflows."""
        ...

    def update_admin_user_role(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        role_action: Literal["grant_admin", "revoke_admin"],
    ) -> dict[str, object] | None:
        """Apply admin role changes for target users with owner safeguards."""
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
    deletion_retention_window: timedelta = timedelta(days=7)

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
        failed_sign_in_raw = account.get("failed_sign_in_count")
        failed_sign_in_count = (
            int(failed_sign_in_raw) if isinstance(failed_sign_in_raw, int | str) else 0
        )

        if lockout_until is not None and lockout_until > now:
            raise ContractQueryError("account_locked")

        if lockout_until is not None and lockout_until <= now and failed_sign_in_count > 0:
            self.repository.update_failed_sign_in(
                user_id=str(account["user_id"]),
                failed_sign_in_count=0,
                lockout_until=None,
            )
            failed_sign_in_count = 0

        if not self._verify_password(password, str(account.get("password_hash") or "")):
            failed_sign_in_count += 1
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
            if lockout_expires is not None:
                self.repository.write_audit_event(
                    event_type="lockout_applied",
                    user_id=str(account["user_id"]),
                    actor_user_id=str(account["user_id"]),
                    event_context={
                        "failed_sign_in_count": failed_sign_in_count,
                        "lockout_until": lockout_expires.isoformat(),
                    },
                )
                raise ContractQueryError("account_locked")

            self.repository.write_audit_event(
                event_type="sign_in_failure",
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

    def get_account_navigation(self, *, user_id: str) -> AccountNavigationResponse:
        """Return account-surface navigation metadata for current user."""
        account = self.repository.get_user_by_id(user_id=user_id)
        if account is None:
            raise ContractQueryError("account_not_found")

        privilege_level = cast(
            Literal["user", "admin", "owner"],
            str(account.get("privilege_level") or "user"),
        )
        show_admin_entry = privilege_level in {"admin", "owner"}
        if privilege_level == "owner":
            role_chip = "Owner"
        elif privilege_level == "admin":
            role_chip = "Admin"
        else:
            role_chip = None
        return AccountNavigationResponse(
            account_route="/settings",
            show_admin_entry=show_admin_entry,
            admin_route="/admin" if show_admin_entry else None,
            role_chip=role_chip,
            privilege_level=privilege_level,
        )

    def get_admin_navigation(self, *, user_id: str) -> AdminNavigationResponse:
        """Return ordered admin-only destination list for admins and owners."""
        account = self.repository.get_user_by_id(user_id=user_id)
        if account is None:
            raise ContractQueryError("account_not_found")

        privilege_level = str(account.get("privilege_level") or "user")
        if privilege_level not in {"admin", "owner"}:
            raise ContractQueryError("forbidden")

        return AdminNavigationResponse(
            items=[
                AdminNavigationItem(
                    item_key="admin_users",
                    label="Users",
                    route="/admin/users",
                    description="Manage account status, sessions, and admin roles.",
                )
            ]
        )

    def update_admin_user_status(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        account_status: Literal["active", "deactivated"],
    ) -> AdminUserSummary:
        """Update a user's lifecycle status from admin controls."""
        if account_status not in {"active", "deactivated"}:
            raise ContractQueryError("account_status must be active or deactivated")

        updated, revoked_count = self.repository.update_admin_user_status(
            actor_user_id=actor_user_id,
            user_id=user_id,
            account_status=account_status,
        )
        if updated is None:
            raise ContractQueryError("account_not_found")

        event_type = "account_reactivated" if account_status == "active" else "account_deactivated"
        self.repository.write_audit_event(
            event_type=event_type,
            user_id=user_id,
            actor_user_id=actor_user_id,
            event_context={
                "account_status": account_status,
                "revoked_session_count": revoked_count,
            },
        )
        return AdminUserSummary.model_validate(updated)

    def admin_revoke_user_sessions(self, *, actor_user_id: str, user_id: str) -> int:
        """Revoke all active sessions for a target user from admin controls."""
        account = self.repository.get_user_by_id(user_id=user_id)
        if account is None:
            raise ContractQueryError("account_not_found")

        revoked_count = self.repository.revoke_all_sessions_for_user_as_admin(
            user_id=user_id,
            reason="admin_revoke",
        )
        self.repository.write_audit_event(
            event_type="session_revoked",
            user_id=user_id,
            actor_user_id=actor_user_id,
            event_context={
                "reason": "admin_revoke",
                "revoked_session_count": revoked_count,
            },
        )
        return revoked_count

    def update_admin_user_role(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        role_action: Literal["grant_admin", "revoke_admin"],
    ) -> AdminUserSummary:
        """Apply role-governance updates with owner-protected invariants."""
        if role_action not in {"grant_admin", "revoke_admin"}:
            raise ContractQueryError("role_action must be grant_admin or revoke_admin")

        updated = self.repository.update_admin_user_role(
            actor_user_id=actor_user_id,
            user_id=user_id,
            role_action=role_action,
        )
        if updated is None:
            raise ContractQueryError("account_not_found")

        return AdminUserSummary.model_validate(updated)

    def get_account_profile(self, *, user_id: str) -> ProfileResponse:
        """Return the current user's persisted profile details."""
        account = self.repository.get_user_by_id(user_id=user_id)
        if account is None:
            raise ContractQueryError("account_not_found")
        return self._profile_response(account)

    def update_account_profile(
        self,
        *,
        user_id: str,
        email: str | None,
        display_name: str | None,
    ) -> ProfileResponse:
        """Persist profile updates for the current user and return latest profile."""
        normalized_email = normalize_optional_email(email)
        normalized_display_name = normalize_display_name(display_name)
        updated = self.repository.update_user_profile(
            user_id=user_id,
            email=normalized_email,
            display_name=normalized_display_name,
        )
        if updated is None:
            raise ContractQueryError("account_not_found")
        return self._profile_response(updated)

    def change_account_password(
        self,
        *,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> None:
        """Rotate password hash and revoke all active sessions for the account."""
        account = self.repository.get_user_by_id(user_id=user_id)
        if account is None:
            raise ContractQueryError("account_not_found")

        ensure_account_active(str(account["account_status"]))

        if not self._verify_password(current_password, str(account.get("password_hash") or "")):
            raise ContractQueryError("invalid_credentials")

        validate_password_strength(new_password)
        revoked_count = self.repository.change_password_and_revoke_sessions(
            user_id=user_id,
            password_hash=self._hash_password(new_password),
            reason="password_changed",
        )
        self.repository.write_audit_event(
            event_type="password_changed",
            user_id=user_id,
            actor_user_id=user_id,
            event_context={"revoked_session_count": revoked_count},
        )

    def request_account_deletion(self, *, user_id: str) -> DeletionRequestResponse:
        """Mark account for deletion and revoke all active sessions immediately."""
        account = self.repository.get_user_by_id(user_id=user_id)
        if account is None:
            raise ContractQueryError("account_not_found")
        account_status = str(account.get("account_status") or "")
        if account_status == "deleted":
            raise ContractQueryError("account_not_found")

        now = datetime.now(tz=UTC)
        default_due_at = (now + self.deletion_retention_window).replace(microsecond=0).isoformat()
        updated = self.repository.request_account_deletion(
            user_id=user_id,
            deletion_due_at=default_due_at,
        )
        if updated is None:
            raise ContractQueryError("account_not_found")

        deletion_due_at = str(updated.get("deletion_due_at") or default_due_at)
        revoked_count = self.repository.revoke_all_sessions_for_user(
            user_id=user_id,
            reason="deletion_requested",
        )
        self.repository.write_audit_event(
            event_type="deletion_requested",
            user_id=user_id,
            actor_user_id=user_id,
            event_context={
                "deletion_due_at": deletion_due_at,
                "revoked_session_count": revoked_count,
            },
        )

        return DeletionRequestResponse(
            user_id=user_id,
            account_status="deletion_pending",
            deletion_due_at=deletion_due_at,
        )

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
                privilege_level=cast(
                    Literal["user", "admin", "owner"],
                    str(account.get("privilege_level") or "user"),
                ),
            ),
            session=SessionSummary.model_validate(session_payload),
        )

    @staticmethod
    def _profile_response(account: dict[str, object]) -> ProfileResponse:
        return ProfileResponse(
            user_id=str(account["user_id"]),
            email=str(account["email"]),
            display_name=(
                str(account["display_name"]) if account.get("display_name") is not None else None
            ),
            account_status=cast(
                Literal["active", "deactivated", "deletion_pending", "deleted"],
                str(account["account_status"]),
            ),
            is_admin=bool(account.get("is_admin") or False),
            privilege_level=cast(
                Literal["user", "admin", "owner"],
                str(account.get("privilege_level") or "user"),
            ),
            updated_at=str(account.get("updated_at") or datetime.now(tz=UTC).isoformat()),
        )

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @classmethod
    def _verify_password(cls, password: str, persisted_hash: str) -> bool:
        return cls._hash_password(password) == persisted_hash
