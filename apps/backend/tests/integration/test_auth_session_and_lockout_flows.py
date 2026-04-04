"""Integration-style coverage for auth session creation and lockout policy."""

# ruff: noqa: D103

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import cast

import pytest

from src.contract.errors import ContractQueryError
from src.query.auth_management_service import AuthManagementService

_EXPECTED_SESSIONS = 2
_LOCKOUT_THRESHOLD = 3


class _RepoIntegrationDouble:
    def __init__(self) -> None:
        self.user_id = "user-1"
        self.password_hash = AuthManagementService._hash_password("verysecure123")
        self.user: dict[str, object] = {
            "user_id": self.user_id,
            "email": "user@example.com",
            "email_normalized": "user@example.com",
            "display_name": "User",
            "account_status": "active",
            "privilege_level": "user",
            "failed_sign_in_count": 0,
            "lockout_until": None,
            "password_hash": self.password_hash,
            "is_admin": False,
            "updated_at": datetime.now(tz=UTC).isoformat(),
        }
        self.sessions: list[dict[str, object]] = []
        self.failed_sign_in_updates: list[dict[str, object]] = []

    def create_user_account(
        self,
        *,
        email: str,
        password_hash: str,
        display_name: str | None,
        is_admin: bool,
    ) -> dict[str, object]:
        self.user = {
            **self.user,
            "email": email,
            "email_normalized": email,
            "display_name": display_name,
            "password_hash": password_hash,
            "is_admin": is_admin,
            "privilege_level": "admin" if is_admin else "user",
        }
        return self.user

    def get_user_by_email(self, *, email: str) -> dict[str, object] | None:
        if email != str(self.user["email_normalized"]):
            return None
        return self.user

    def get_user_by_id(self, *, user_id: str) -> dict[str, object] | None:
        return self.user if user_id == self.user_id else None

    def update_failed_sign_in(
        self,
        *,
        user_id: str,
        failed_sign_in_count: int,
        lockout_until: str | None,
    ) -> None:
        self.failed_sign_in_updates.append(
            {
                "user_id": user_id,
                "failed_sign_in_count": failed_sign_in_count,
                "lockout_until": lockout_until,
            }
        )
        self.user["failed_sign_in_count"] = failed_sign_in_count
        self.user["lockout_until"] = lockout_until

    def update_password_hash(self, *, user_id: str, password_hash: str) -> None:
        self.password_hash = password_hash
        self.user["password_hash"] = password_hash

    def update_user_profile(
        self,
        *,
        user_id: str,
        email: str | None,
        display_name: str | None,
    ) -> dict[str, object] | None:
        if email is not None:
            self.user["email"] = email
            self.user["email_normalized"] = email
        self.user["display_name"] = display_name
        self.user["updated_at"] = datetime.now(tz=UTC).isoformat()
        return self.user

    def change_password_and_revoke_sessions(
        self,
        *,
        user_id: str,
        password_hash: str,
        reason: str,
    ) -> int:
        self.user["password_hash"] = password_hash
        return 0

    def request_account_deletion(
        self,
        *,
        user_id: str,
        deletion_due_at: str,
    ) -> dict[str, object] | None:
        self.user["account_status"] = "deletion_pending"
        self.user["deletion_due_at"] = deletion_due_at
        return self.user

    def create_session(
        self,
        *,
        user_id: str,
        expires_at: str,
        client_metadata: dict[str, object] | None,
    ) -> dict[str, object]:
        session_id = f"session-{len(self.sessions) + 1}"
        payload = {
            "session_id": session_id,
            "created_at": datetime.now(tz=UTC).isoformat(),
            "expires_at": expires_at,
            "session_status": "active",
            "client_label": (
                str(client_metadata.get("client_label"))
                if isinstance(client_metadata, dict)
                else None
            ),
            "user_id": user_id,
            "user": {
                "user_id": self.user_id,
                "email": str(self.user["email"]),
                "display_name": self.user.get("display_name"),
                "account_status": str(self.user["account_status"]),
                "is_admin": bool(self.user.get("is_admin") or False),
                "privilege_level": str(self.user.get("privilege_level") or "user"),
            },
        }
        typed_payload = cast(dict[str, object], payload)
        self.sessions.append(typed_payload)
        return typed_payload

    def get_active_session(self, *, session_id: str) -> dict[str, object] | None:
        for session in self.sessions:
            if session["session_id"] == session_id:
                return session
        return None

    def list_active_sessions(self, *, user_id: str) -> list[dict[str, object]]:
        return []

    def revoke_session(self, *, user_id: str, session_id: str, reason: str) -> bool:
        return True

    def revoke_all_sessions_for_user(self, *, user_id: str, reason: str) -> int:
        return 0

    def list_admin_users(self) -> list[dict[str, object]]:
        return []

    def update_admin_user_status(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        account_status: str,
    ) -> tuple[dict[str, object] | None, int]:
        if user_id != self.user_id:
            return None, 0
        self.user["account_status"] = account_status
        return self.user, 0

    def revoke_all_sessions_for_user_as_admin(self, *, user_id: str, reason: str) -> int:
        return self.revoke_all_sessions_for_user(user_id=user_id, reason=reason)

    def update_admin_user_role(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        role_action: str,
    ) -> dict[str, object] | None:
        return self.user

    def write_audit_event(
        self,
        *,
        event_type: str,
        user_id: str | None,
        actor_user_id: str | None,
        event_context: dict[str, object] | None,
    ) -> None:
        return None


def test_allows_multiple_sessions_for_same_user() -> None:
    repo = _RepoIntegrationDouble()
    service = AuthManagementService(repository=repo)

    first = service.login(
        email="user@example.com",
        password="verysecure123",
        client_metadata={"client_label": "Browser A"},
    )
    second = service.login(
        email="user@example.com",
        password="verysecure123",
        client_metadata={"client_label": "Browser B"},
    )

    assert first.session.session_id != second.session.session_id
    assert len(repo.sessions) == _EXPECTED_SESSIONS


def test_enforces_lockout_threshold_and_window_expiry_reset() -> None:
    repo = _RepoIntegrationDouble()
    service = AuthManagementService(
        repository=repo,
        lockout_threshold=_LOCKOUT_THRESHOLD,
        lockout_window=timedelta(minutes=5),
    )

    with pytest.raises(ContractQueryError, match="invalid_credentials"):
        service.login(email="user@example.com", password="wrong")
    with pytest.raises(ContractQueryError, match="invalid_credentials"):
        service.login(email="user@example.com", password="wrong")
    with pytest.raises(ContractQueryError, match="account_locked"):
        service.login(email="user@example.com", password="wrong")

    assert repo.failed_sign_in_updates[-1]["failed_sign_in_count"] == _LOCKOUT_THRESHOLD
    assert repo.failed_sign_in_updates[-1]["lockout_until"] is not None

    with pytest.raises(ContractQueryError, match="account_locked"):
        service.login(email="user@example.com", password="verysecure123")

    repo.user["lockout_until"] = (datetime.now(tz=UTC) - timedelta(seconds=5)).isoformat()
    response = service.login(email="user@example.com", password="verysecure123")

    assert response.session.session_id.startswith("session-")
    assert repo.failed_sign_in_updates[-2]["failed_sign_in_count"] == 0
    assert repo.failed_sign_in_updates[-1]["failed_sign_in_count"] == 0
