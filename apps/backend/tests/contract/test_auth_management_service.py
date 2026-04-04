"""Unit coverage for auth/account service orchestration workflows."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal, cast

import pytest

from src.contract.errors import ContractQueryError
from src.query.auth_management_service import AuthManagementService


class _RepoDouble:
    def __init__(self) -> None:
        now = datetime.now(tz=UTC).isoformat()
        self.users_by_email: dict[str, dict[str, object]] = {}
        self.users_by_id: dict[str, dict[str, object]] = {}
        self.sessions: dict[str, dict[str, object]] = {}
        self.last_user_id = 0
        self.audit_events: list[dict[str, object]] = []
        self.failed_sign_in_updates: list[dict[str, object]] = []
        self.revocations: list[tuple[str, str, str]] = []
        self.admin_users = [
            {
                "user_id": "admin-1",
                "email": "admin@example.com",
                "display_name": "Admin",
                "account_status": "active",
                "is_admin": True,
                "privilege_level": "admin",
                "updated_at": now,
            }
        ]

    def create_user_account(
        self,
        *,
        email: str,
        password_hash: str,
        display_name: str | None,
        is_admin: bool,
    ) -> dict[str, object]:
        self.last_user_id += 1
        user_id = f"user-{self.last_user_id}"
        payload = {
            "user_id": user_id,
            "email": email,
            "email_normalized": email,
            "display_name": display_name,
            "account_status": "active",
            "privilege_level": "admin" if is_admin else "user",
            "failed_sign_in_count": 0,
            "lockout_until": None,
            "password_hash": password_hash,
            "is_admin": is_admin,
            "updated_at": datetime.now(tz=UTC).isoformat(),
        }
        typed_payload = cast(dict[str, object], payload)
        self.users_by_email[email] = typed_payload
        self.users_by_id[user_id] = typed_payload
        return typed_payload

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
        self.failed_sign_in_updates.append(
            {
                "user_id": user_id,
                "failed_sign_in_count": failed_sign_in_count,
                "lockout_until": lockout_until,
            }
        )
        if user_id in self.users_by_id:
            self.users_by_id[user_id]["failed_sign_in_count"] = failed_sign_in_count
            self.users_by_id[user_id]["lockout_until"] = lockout_until

    def update_password_hash(self, *, user_id: str, password_hash: str) -> None:
        if user_id in self.users_by_id:
            self.users_by_id[user_id]["password_hash"] = password_hash

    def update_user_profile(
        self,
        *,
        user_id: str,
        email: str | None,
        display_name: str | None,
    ) -> dict[str, object] | None:
        user = self.users_by_id.get(user_id)
        if user is None:
            return None
        if email is not None:
            user["email"] = email
            user["email_normalized"] = email
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
        self.update_password_hash(user_id=user_id, password_hash=password_hash)
        return self.revoke_all_sessions_for_user(user_id=user_id, reason=reason)

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
        }
        self.sessions[session_id] = {
            **payload,
            "user_id": user_id,
            "user": {
                "user_id": user_id,
                "email": str(self.users_by_id[user_id]["email"]),
                "display_name": self.users_by_id[user_id]["display_name"],
                "account_status": self.users_by_id[user_id]["account_status"],
                "is_admin": bool(self.users_by_id[user_id]["is_admin"]),
                "privilege_level": str(self.users_by_id[user_id].get("privilege_level") or "user"),
            },
        }
        return cast(dict[str, object], payload)

    def get_active_session(self, *, session_id: str) -> dict[str, object] | None:
        return self.sessions.get(session_id)

    def list_active_sessions(self, *, user_id: str) -> list[dict[str, object]]:
        return [
            {
                "session_id": str(value["session_id"]),
                "created_at": str(value["created_at"]),
                "expires_at": str(value["expires_at"]),
                "session_status": "active",
                "client_label": value.get("client_label"),
            }
            for value in self.sessions.values()
            if value.get("user_id") == user_id
        ]

    def revoke_session(self, *, user_id: str, session_id: str, reason: str) -> bool:
        self.revocations.append((user_id, session_id, reason))
        return session_id in self.sessions

    def revoke_all_sessions_for_user(self, *, user_id: str, reason: str) -> int:
        return len(self.list_active_sessions(user_id=user_id))

    def list_admin_users(self) -> list[dict[str, object]]:
        return cast(list[dict[str, object]], self.admin_users)

    def update_admin_user_status(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        account_status: str,
    ) -> tuple[dict[str, object] | None, int]:
        user = self.users_by_id.get(user_id)
        if user is None:
            return None, 0
        user["account_status"] = account_status
        user["updated_at"] = datetime.now(tz=UTC).isoformat()
        revoked_count = (
            len(self.list_active_sessions(user_id=user_id))
            if account_status == "deactivated"
            else 0
        )
        return user, revoked_count

    def revoke_all_sessions_for_user_as_admin(self, *, user_id: str, reason: str) -> int:
        return self.revoke_all_sessions_for_user(user_id=user_id, reason=reason)

    def update_admin_user_role(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        role_action: str,
    ) -> dict[str, object] | None:
        user = self.users_by_id.get(user_id)
        if user is None:
            return None
        if str(user.get("privilege_level") or "user") == "owner":
            raise ContractQueryError("owner_role_protected")
        if role_action == "grant_admin":
            user["is_admin"] = True
            user["privilege_level"] = "admin"
        elif role_action == "revoke_admin":
            user["is_admin"] = False
            user["privilege_level"] = "user"
        else:
            raise ContractQueryError("role_action must be grant_admin or revoke_admin")
        user["updated_at"] = datetime.now(tz=UTC).isoformat()
        return user

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


def _service_and_repo() -> tuple[AuthManagementService, _RepoDouble]:
    repo = _RepoDouble()
    service = AuthManagementService(repository=repo)
    return service, repo


def test_register_and_login_happy_path() -> None:
    """Register and login should return user/session payloads."""
    service, repo = _service_and_repo()

    register = service.register_account(
        email="user@example.com",
        password="verysecure123",
        display_name="User",
        client_metadata={"client_label": "Browser"},
    )
    login = service.login(
        email="user@example.com",
        password="verysecure123",
        client_metadata={"client_label": "Browser"},
    )

    assert register.user.user_id == "user-1"
    assert login.user.email == "user@example.com"
    assert len(repo.audit_events) > 1


def test_register_rejects_duplicate_and_login_rejects_bad_password() -> None:
    """Duplicate registration and invalid credentials should raise contract errors."""
    service, repo = _service_and_repo()

    service.register_account(
        email="user@example.com",
        password="verysecure123",
        display_name="User",
    )

    with pytest.raises(ContractQueryError):
        service.register_account(
            email="user@example.com",
            password="verysecure123",
            display_name="User",
        )

    with pytest.raises(ContractQueryError):
        service.login(email="user@example.com", password="wrongpassword")

    assert repo.failed_sign_in_updates[-1]["failed_sign_in_count"] == 1


def test_authenticate_logout_and_session_listing() -> None:
    """Authenticate session, list sessions, and logout workflow should succeed."""
    service, _repo = _service_and_repo()
    register = service.register_account(
        email="user@example.com",
        password="verysecure123",
        display_name="User",
    )

    session = service.authenticate_session(session_id=register.session.session_id)
    listed = service.list_user_sessions(user_id=register.user.user_id)
    service.logout(
        user_id=register.user.user_id,
        session_id=register.session.session_id,
    )

    assert session["session_id"] == register.session.session_id
    assert listed.items[0].session_id == register.session.session_id


def test_revoke_session_and_admin_list_paths() -> None:
    """Exercise revoke-session and admin-list service paths."""
    service, repo = _service_and_repo()
    register = service.register_account(
        email="user@example.com",
        password="verysecure123",
        display_name="User",
    )

    service.revoke_user_session(
        user_id=register.user.user_id,
        session_id=register.session.session_id,
    )
    admin_users = service.list_admin_users()

    assert repo.revocations[-1][2] == "user_revoke"
    assert admin_users.items[0].is_admin is True


def test_navigation_and_role_update_paths() -> None:
    """Cover account/admin navigation responses and role update happy path."""
    service, repo = _service_and_repo()
    register = service.register_account(
        email="user@example.com",
        password="verysecure123",
        display_name="User",
    )

    account_navigation = service.get_account_navigation(user_id=register.user.user_id)
    assert account_navigation.account_route == "/settings"
    assert account_navigation.show_admin_entry is False

    with pytest.raises(ContractQueryError, match="forbidden"):
        service.get_admin_navigation(user_id=register.user.user_id)

    repo.users_by_id["admin-1"] = {
        "user_id": "admin-1",
        "email": "admin@example.com",
        "email_normalized": "admin@example.com",
        "display_name": "Admin",
        "account_status": "active",
        "failed_sign_in_count": 0,
        "lockout_until": None,
        "password_hash": AuthManagementService._hash_password("verysecure123"),
        "is_admin": True,
        "privilege_level": "admin",
        "updated_at": datetime.now(tz=UTC).isoformat(),
    }
    admin_navigation = service.get_admin_navigation(user_id="admin-1")
    assert admin_navigation.items[0].route == "/admin/users"

    role_updated = service.update_admin_user_role(
        actor_user_id="admin-1",
        user_id=register.user.user_id,
        role_action="grant_admin",
    )
    assert role_updated.is_admin is True
    assert role_updated.privilege_level == "admin"


def test_profile_updates_and_missing_account_paths() -> None:
    """Validate profile updates and missing-account lookup error path."""
    service, _repo = _service_and_repo()
    register = service.register_account(
        email="user@example.com",
        password="verysecure123",
        display_name="User",
    )

    updated = service.update_account_profile(
        user_id=register.user.user_id,
        email="updated@example.com",
        display_name="Updated User",
    )
    assert updated.email == "updated@example.com"
    assert updated.display_name == "Updated User"

    with pytest.raises(ContractQueryError, match="account_not_found"):
        service.get_account_profile(user_id="missing-user")


def test_role_update_rejects_missing_and_invalid_actions() -> None:
    """Reject admin-role updates for missing users and invalid role actions."""
    service, _repo = _service_and_repo()
    with pytest.raises(ContractQueryError, match="account_not_found"):
        service.update_admin_user_role(
            actor_user_id="admin-1",
            user_id="missing-user",
            role_action="grant_admin",
        )

    with pytest.raises(ContractQueryError, match="role_action must be grant_admin or revoke_admin"):
        service.update_admin_user_role(
            actor_user_id="admin-1",
            user_id="missing-user",
            role_action=cast(Literal["grant_admin", "revoke_admin"], "invalid"),
        )


def test_password_and_deletion_missing_account_paths() -> None:
    """Return account-not-found for password/deletion calls on unknown users."""
    service, _repo = _service_and_repo()

    with pytest.raises(ContractQueryError, match="account_not_found"):
        service.change_account_password(
            user_id="missing-user",
            current_password="oldpassword123",
            new_password="newpassword123",
        )

    with pytest.raises(ContractQueryError, match="account_not_found"):
        service.request_account_deletion(user_id="missing-user")


def test_authenticate_requires_valid_session_and_active_account() -> None:
    """Invalid sessions and inactive accounts should fail authentication checks."""
    service, repo = _service_and_repo()
    register = service.register_account(
        email="user@example.com",
        password="verysecure123",
        display_name="User",
    )

    repo.users_by_id[register.user.user_id]["account_status"] = "deactivated"
    session_user = cast(
        dict[str, object],
        repo.sessions[register.session.session_id]["user"],
    )
    session_user["account_status"] = "deactivated"

    with pytest.raises(ContractQueryError):
        service.authenticate_session(session_id=register.session.session_id)

    with pytest.raises(ContractQueryError):
        service.authenticate_session(session_id="missing-session")
