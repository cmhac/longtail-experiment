"""Integration-style coverage for admin user-management runtime behavior."""

# ruff: noqa: D103

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.contract.errors import ContractQueryError
from src.query.auth_management_service import AuthManagementService

_EXPECTED_REVOKED_SESSIONS = 2


class _RepoIntegrationDouble:
    def __init__(self) -> None:
        now = datetime.now(tz=UTC).isoformat()
        self.users: dict[str, dict[str, object]] = {
            "admin-1": {
                "user_id": "admin-1",
                "email": "admin@example.com",
                "email_normalized": "admin@example.com",
                "display_name": "Admin",
                "account_status": "active",
                "failed_sign_in_count": 0,
                "lockout_until": None,
                "password_hash": AuthManagementService._hash_password("adminpassword123"),
                "is_admin": True,
                "updated_at": now,
            },
            "user-1": {
                "user_id": "user-1",
                "email": "user@example.com",
                "email_normalized": "user@example.com",
                "display_name": "User",
                "account_status": "active",
                "failed_sign_in_count": 0,
                "lockout_until": None,
                "password_hash": AuthManagementService._hash_password("userpassword123"),
                "is_admin": False,
                "updated_at": now,
            },
        }
        self.sessions_by_user: dict[str, list[str]] = {
            "admin-1": ["admin-session"],
            "user-1": ["user-session-a", "user-session-b"],
        }
        self.audit_events: list[dict[str, object]] = []

    def create_user_account(self, **kwargs: object) -> dict[str, object]:
        return self.users["user-1"]

    def get_user_by_email(self, *, email: str) -> dict[str, object] | None:
        for user in self.users.values():
            if user["email_normalized"] == email:
                return user
        return None

    def get_user_by_id(self, *, user_id: str) -> dict[str, object] | None:
        return self.users.get(user_id)

    def update_failed_sign_in(
        self,
        *,
        user_id: str,
        failed_sign_in_count: int,
        lockout_until: str | None,
    ) -> None:
        self.users[user_id]["failed_sign_in_count"] = failed_sign_in_count
        self.users[user_id]["lockout_until"] = lockout_until

    def update_password_hash(self, *, user_id: str, password_hash: str) -> None:
        self.users[user_id]["password_hash"] = password_hash

    def update_user_profile(
        self,
        *,
        user_id: str,
        display_name: str | None,
    ) -> dict[str, object] | None:
        user = self.users.get(user_id)
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
        self.users[user_id]["password_hash"] = password_hash
        revoked = len(self.sessions_by_user.get(user_id, []))
        self.sessions_by_user[user_id] = []
        return revoked

    def request_account_deletion(
        self,
        *,
        user_id: str,
        deletion_due_at: str,
    ) -> dict[str, object] | None:
        user = self.users.get(user_id)
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
        session_id = f"session-{len(self.sessions_by_user.get(user_id, [])) + 1}"
        self.sessions_by_user.setdefault(user_id, []).append(session_id)
        return {
            "session_id": session_id,
            "created_at": datetime.now(tz=UTC).isoformat(),
            "expires_at": expires_at,
            "session_status": "active",
            "client_label": None,
        }

    def get_active_session(self, *, session_id: str) -> dict[str, object] | None:
        for user_id, sessions in self.sessions_by_user.items():
            if session_id in sessions:
                user = self.users[user_id]
                return {
                    "session_id": session_id,
                    "user": {
                        "user_id": user_id,
                        "email": user["email"],
                        "display_name": user["display_name"],
                        "account_status": user["account_status"],
                        "is_admin": user["is_admin"],
                    },
                }
        return None

    def list_active_sessions(self, *, user_id: str) -> list[dict[str, object]]:
        return [
            {
                "session_id": session_id,
                "created_at": datetime.now(tz=UTC).isoformat(),
                "expires_at": datetime.now(tz=UTC).isoformat(),
                "session_status": "active",
                "client_label": None,
            }
            for session_id in self.sessions_by_user.get(user_id, [])
        ]

    def revoke_session(self, *, user_id: str, session_id: str, reason: str) -> bool:
        sessions = self.sessions_by_user.get(user_id, [])
        if session_id not in sessions:
            return False
        sessions.remove(session_id)
        return True

    def revoke_all_sessions_for_user(self, *, user_id: str, reason: str) -> int:
        revoked = len(self.sessions_by_user.get(user_id, []))
        self.sessions_by_user[user_id] = []
        return revoked

    def list_admin_users(self) -> list[dict[str, object]]:
        return [
            {
                "user_id": user["user_id"],
                "email": user["email"],
                "display_name": user["display_name"],
                "account_status": user["account_status"],
                "is_admin": user["is_admin"],
                "updated_at": str(user["updated_at"]),
            }
            for user in self.users.values()
        ]

    def update_admin_user_status(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        account_status: str,
    ) -> tuple[dict[str, object] | None, int]:
        user = self.users.get(user_id)
        if user is None:
            return None, 0

        if (
            user["is_admin"]
            and account_status == "deactivated"
            and user["account_status"] == "active"
            and sum(
                1
                for value in self.users.values()
                if (
                    value["is_admin"]
                    and value["account_status"] == "active"
                    and value["user_id"] != user_id
                )
            )
            == 0
        ):
            raise ContractQueryError("final_admin_guard")

        user["account_status"] = account_status
        user["updated_at"] = datetime.now(tz=UTC).isoformat()
        revoked = 0
        if account_status == "deactivated":
            revoked = len(self.sessions_by_user.get(user_id, []))
            self.sessions_by_user[user_id] = []
        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "display_name": user["display_name"],
            "account_status": user["account_status"],
            "is_admin": user["is_admin"],
            "updated_at": str(user["updated_at"]),
        }, revoked

    def revoke_all_sessions_for_user_as_admin(self, *, user_id: str, reason: str) -> int:
        return self.revoke_all_sessions_for_user(user_id=user_id, reason=reason)

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


def test_admin_deactivation_revokes_sessions_and_blocks_login_until_reactivated() -> None:
    repo = _RepoIntegrationDouble()
    service = AuthManagementService(repository=repo)

    deactivated = service.update_admin_user_status(
        actor_user_id="admin-1",
        user_id="user-1",
        account_status="deactivated",
    )
    assert deactivated.account_status == "deactivated"
    assert repo.sessions_by_user["user-1"] == []

    with pytest.raises(ContractQueryError, match="account is not active"):
        service.login(email="user@example.com", password="userpassword123")

    reactivated = service.update_admin_user_status(
        actor_user_id="admin-1",
        user_id="user-1",
        account_status="active",
    )
    assert reactivated.account_status == "active"

    login = service.login(email="user@example.com", password="userpassword123")
    assert login.user.user_id == "user-1"


def test_final_active_admin_cannot_be_deactivated() -> None:
    repo = _RepoIntegrationDouble()
    service = AuthManagementService(repository=repo)

    with pytest.raises(ContractQueryError, match="final_admin_guard"):
        service.update_admin_user_status(
            actor_user_id="admin-1",
            user_id="admin-1",
            account_status="deactivated",
        )


def test_admin_can_revoke_target_user_sessions() -> None:
    repo = _RepoIntegrationDouble()
    service = AuthManagementService(repository=repo)

    revoked_count = service.admin_revoke_user_sessions(actor_user_id="admin-1", user_id="user-1")
    assert revoked_count == _EXPECTED_REVOKED_SESSIONS
    assert repo.sessions_by_user["user-1"] == []
