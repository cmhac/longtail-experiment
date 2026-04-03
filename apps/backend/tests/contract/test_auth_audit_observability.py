"""Contract tests for auth audit observability behavior."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

import pytest

from src.contract.errors import ContractQueryError
from src.query.auth_management_service import AuthManagementService


class _ObservabilityRepoDouble:
    def __init__(self) -> None:
        now = datetime.now(tz=UTC).isoformat()
        self.users_by_email: dict[str, dict[str, object]] = {
            "user@example.com": {
                "user_id": "user-1",
                "email": "user@example.com",
                "email_normalized": "user@example.com",
                "display_name": "User",
                "account_status": "active",
                "failed_sign_in_count": 0,
                "lockout_until": None,
                "password_hash": AuthManagementService._hash_password("verysecure123"),
                "is_admin": False,
                "updated_at": now,
            }
        }
        self.users_by_id: dict[str, dict[str, object]] = {
            "user-1": self.users_by_email["user@example.com"]
        }
        self.audit_events: list[dict[str, object]] = []

    def create_user_account(
        self,
        *,
        email: str,
        password_hash: str,
        display_name: str | None,
        is_admin: bool,
    ) -> dict[str, object]:
        account = {
            "user_id": "user-created",
            "email": email,
            "email_normalized": email,
            "display_name": display_name,
            "account_status": "active",
            "failed_sign_in_count": 0,
            "lockout_until": None,
            "password_hash": password_hash,
            "is_admin": is_admin,
            "updated_at": datetime.now(tz=UTC).isoformat(),
        }
        typed_account = cast(dict[str, object], account)
        self.users_by_email[email] = typed_account
        self.users_by_id["user-created"] = typed_account
        return typed_account

    def get_user_by_email(self, *, email: str) -> dict[str, object] | None:
        return self.users_by_email.get(email)

    def get_user_by_id(self, *, user_id: str) -> dict[str, object] | None:
        return self.users_by_id.get(user_id)

    def update_failed_sign_in(
        self,
        *,
        user_id: str,
        failed_sign_in_count: int,
        lockout_until: str | None,
    ) -> None:
        user = self.users_by_id[user_id]
        user["failed_sign_in_count"] = failed_sign_in_count
        user["lockout_until"] = lockout_until

    def update_password_hash(self, *, user_id: str, password_hash: str) -> None:
        self.users_by_id[user_id]["password_hash"] = password_hash

    def update_user_profile(
        self,
        *,
        user_id: str,
        display_name: str | None,
    ) -> dict[str, object] | None:
        user = self.users_by_id.get(user_id)
        if user is None:
            return None
        user["display_name"] = display_name
        user["updated_at"] = datetime.now(tz=UTC).isoformat()
        return user

    def change_password_and_revoke_sessions(
        self,
        *,
        user_id: str,
        password_hash: str,
        reason: str,
    ) -> int:
        self.users_by_id[user_id]["password_hash"] = password_hash
        return 2

    def request_account_deletion(
        self,
        *,
        user_id: str,
        deletion_due_at: str,
    ) -> dict[str, object] | None:
        user = self.users_by_id.get(user_id)
        if user is None:
            return None
        user["account_status"] = "deletion_pending"
        user["deletion_due_at"] = deletion_due_at
        return user

    def create_session(
        self,
        *,
        user_id: str,
        expires_at: str,
        client_metadata: dict[str, object] | None,
    ) -> dict[str, object]:
        return {
            "session_id": "session-1",
            "created_at": datetime.now(tz=UTC).isoformat(),
            "expires_at": expires_at,
            "session_status": "active",
            "client_label": (
                str(client_metadata.get("client_label"))
                if isinstance(client_metadata, dict)
                else None
            ),
        }

    def get_active_session(self, *, session_id: str) -> dict[str, object] | None:
        return {
            "session_id": session_id,
            "user_id": "user-1",
            "created_at": datetime.now(tz=UTC).isoformat(),
            "expires_at": datetime.now(tz=UTC).isoformat(),
            "session_status": "active",
            "user": {
                "user_id": "user-1",
                "email": "user@example.com",
                "display_name": "User",
                "account_status": "active",
                "is_admin": False,
            },
        }

    def list_active_sessions(self, *, user_id: str) -> list[dict[str, object]]:
        return [
            {
                "session_id": "session-1",
                "created_at": datetime.now(tz=UTC).isoformat(),
                "expires_at": datetime.now(tz=UTC).isoformat(),
                "session_status": "active",
                "client_label": "Browser",
            }
        ]

    def revoke_session(self, *, user_id: str, session_id: str, reason: str) -> bool:
        return True

    def revoke_all_sessions_for_user(self, *, user_id: str, reason: str) -> int:
        return 1

    def list_admin_users(self) -> list[dict[str, object]]:
        return [
            {
                "user_id": "admin-1",
                "email": "admin@example.com",
                "display_name": "Admin",
                "account_status": "active",
                "is_admin": True,
                "created_at": datetime.now(tz=UTC).isoformat(),
                "updated_at": datetime.now(tz=UTC).isoformat(),
            }
        ]

    def update_admin_user_status(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        account_status: str,
    ) -> tuple[dict[str, object] | None, int]:
        return self.users_by_id.get(user_id), 0

    def revoke_all_sessions_for_user_as_admin(self, *, user_id: str, reason: str) -> int:
        return 1

    def write_audit_event(
        self,
        *,
        event_type: str,
        user_id: str | None,
        actor_user_id: str | None,
        event_context: dict[str, object] | None,
    ) -> None:
        self.audit_events.append(
            {
                "event_type": event_type,
                "user_id": user_id,
                "actor_user_id": actor_user_id,
                "event_context": event_context,
            }
        )


def test_auth_login_writes_expected_audit_event_context() -> None:
    """Login and logout should write structured auth audit events."""
    repo = _ObservabilityRepoDouble()
    service = AuthManagementService(repository=repo)

    login_response = service.login(
        email="user@example.com",
        password="verysecure123",
        client_metadata={"client_label": "CLI Test"},
    )
    service.logout(
        user_id=login_response.user.user_id,
        session_id=login_response.session.session_id,
    )

    assert repo.audit_events[0]["event_type"] == "sign_in_success"
    assert repo.audit_events[0]["event_context"] is None
    assert repo.audit_events[1]["event_type"] == "sign_out"
    assert repo.audit_events[1]["event_context"] == {"session_id": "session-1"}


def test_auth_lockout_writes_lockout_observability_details() -> None:
    """Lockout audit event should include threshold and lockout timestamp context."""
    repo = _ObservabilityRepoDouble()
    service = AuthManagementService(repository=repo, lockout_threshold=1)

    with pytest.raises(ContractQueryError):
        service.login(email="user@example.com", password="wrong-password")

    assert len(repo.audit_events) == 1
    assert repo.audit_events[0]["event_type"] == "lockout_applied"
    context = repo.audit_events[0]["event_context"]
    assert isinstance(context, dict)
    typed_context = cast(dict[str, object], context)
    assert typed_context["failed_sign_in_count"] == 1
    assert isinstance(typed_context["lockout_until"], str)
