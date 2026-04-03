"""Integration-style coverage for account settings runtime flows."""

# ruff: noqa: D103

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.contract.errors import ContractQueryError
from src.query.auth_management_service import AuthManagementService

_EXPECTED_DELETION_REVOCATION_CALLS = 2


class _RepoIntegrationDouble:
    def __init__(self) -> None:
        now = datetime.now(tz=UTC).isoformat()
        self.user_id = "user-1"
        self.password_hash = AuthManagementService._hash_password("oldpassword123")
        self.user: dict[str, object] = {
            "user_id": self.user_id,
            "email": "user@example.com",
            "email_normalized": "user@example.com",
            "display_name": "User",
            "account_status": "active",
            "failed_sign_in_count": 0,
            "lockout_until": None,
            "password_hash": self.password_hash,
            "is_admin": False,
            "updated_at": now,
            "deletion_due_at": None,
        }
        self.active_sessions = ["session-1", "session-2"]
        self.revoked_all_calls: list[tuple[str, str]] = []
        self.audit_events: list[dict[str, object]] = []
        self.password_rotation_calls: list[dict[str, object]] = []

    def create_user_account(self, **kwargs: object) -> dict[str, object]:
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
        self.user["failed_sign_in_count"] = failed_sign_in_count
        self.user["lockout_until"] = lockout_until

    def update_password_hash(self, *, user_id: str, password_hash: str) -> None:
        self.user["password_hash"] = password_hash

    def update_user_profile(
        self,
        *,
        user_id: str,
        display_name: str | None,
    ) -> dict[str, object] | None:
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
        self.password_rotation_calls.append(
            {
                "user_id": user_id,
                "password_hash": password_hash,
                "reason": reason,
            }
        )
        self.user["password_hash"] = password_hash
        revoked_count = len(self.active_sessions)
        self.active_sessions.clear()
        return revoked_count

    def request_account_deletion(
        self,
        *,
        user_id: str,
        deletion_due_at: str,
    ) -> dict[str, object] | None:
        if self.user["account_status"] != "deletion_pending":
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
        return {
            "session_id": "session-created",
            "created_at": datetime.now(tz=UTC).isoformat(),
            "expires_at": expires_at,
            "session_status": "active",
            "client_label": None,
        }

    def get_active_session(self, *, session_id: str) -> dict[str, object] | None:
        return None

    def list_active_sessions(self, *, user_id: str) -> list[dict[str, object]]:
        return []

    def revoke_session(self, *, user_id: str, session_id: str, reason: str) -> bool:
        return True

    def revoke_all_sessions_for_user(self, *, user_id: str, reason: str) -> int:
        self.revoked_all_calls.append((user_id, reason))
        revoked_count = len(self.active_sessions)
        self.active_sessions.clear()
        return revoked_count

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


def test_password_change_rotates_hash_and_revokes_all_sessions() -> None:
    repo = _RepoIntegrationDouble()
    service = AuthManagementService(repository=repo)

    service.change_account_password(
        user_id=repo.user_id,
        current_password="oldpassword123",
        new_password="newpassword123",
    )

    assert repo.password_rotation_calls[-1]["reason"] == "password_changed"
    assert repo.active_sessions == []
    assert repo.audit_events[-1]["event_type"] == "password_changed"


def test_password_change_rejects_invalid_current_password() -> None:
    repo = _RepoIntegrationDouble()
    service = AuthManagementService(repository=repo)

    with pytest.raises(ContractQueryError, match="invalid_credentials"):
        service.change_account_password(
            user_id=repo.user_id,
            current_password="wrong",
            new_password="newpassword123",
        )


def test_deletion_request_sets_pending_status_and_is_idempotent() -> None:
    repo = _RepoIntegrationDouble()
    service = AuthManagementService(repository=repo)

    first = service.request_account_deletion(user_id=repo.user_id)
    second = service.request_account_deletion(user_id=repo.user_id)

    assert first.account_status == "deletion_pending"
    assert second.account_status == "deletion_pending"
    assert first.deletion_due_at == second.deletion_due_at
    assert len(repo.revoked_all_calls) == _EXPECTED_DELETION_REVOCATION_CALLS
    assert repo.audit_events[-1]["event_type"] == "deletion_requested"
