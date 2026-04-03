"""Unit coverage for persisted auth/account repository adapter methods."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import cast
from uuid import uuid4

from sqlalchemy import Engine

from src.query.auth_management_persisted_repository import PersistedAuthManagementRepository


class _Result:
    def __init__(
        self,
        *,
        mappings_first: dict[str, object] | None = None,
        mappings_all: list[dict[str, object]] | None = None,
        scalar_one_or_none: object = None,
        rowcount: int = 0,
    ) -> None:
        self._mappings_first = mappings_first
        self._mappings_all = mappings_all or []
        self._scalar_one_or_none = scalar_one_or_none
        self.rowcount = rowcount

    def mappings(self) -> _Result:
        return self

    def first(self) -> dict[str, object] | None:
        return self._mappings_first

    def all(self) -> list[dict[str, object]]:
        return self._mappings_all

    def scalar_one_or_none(self) -> object:
        return self._scalar_one_or_none


class _ConnectionDouble:
    def __init__(self) -> None:
        self.executed: list[tuple[str, dict[str, object] | None]] = []
        now = datetime.now(tz=UTC)
        self.user_row: dict[str, object] = {
            "id": uuid4(),
            "email": "user@example.com",
            "email_normalized": "user@example.com",
            "display_name": "User",
            "account_status": "active",
            "failed_sign_in_count": 0,
            "lockout_until": None,
            "updated_at": now,
            "password_hash": "hash",
            "is_admin": False,
        }

    def execute(self, statement: object, params: dict[str, object] | None = None) -> _Result:
        sql = str(statement)
        self.executed.append((sql, params))

        result: _Result
        if "WHERE ua.email_normalized" in sql or "WHERE ua.id = :user_id" in sql:
            result = _Result(mappings_first=self.user_row)
        elif "FROM auth_sessions s" in sql:
            result = _Result(
                mappings_first={
                    "id": uuid4(),
                    "user_id": uuid4(),
                    "session_status": "active",
                    "created_at": datetime.now(tz=UTC),
                    "expires_at": datetime.now(tz=UTC),
                    "client_metadata": '{"client_label":"Browser"}',
                    "email": "user@example.com",
                    "display_name": "User",
                    "account_status": "active",
                    "is_admin": False,
                }
            )
        elif "FROM auth_sessions\n                    WHERE user_id" in sql:
            result = _Result(
                mappings_all=[
                    {
                        "id": uuid4(),
                        "created_at": datetime.now(tz=UTC),
                        "expires_at": datetime.now(tz=UTC),
                        "session_status": "active",
                        "client_metadata": {"client_label": "Browser"},
                    }
                ]
            )
        elif "UPDATE auth_sessions" in sql and "RETURNING id" in sql:
            result = _Result(scalar_one_or_none=uuid4())
        elif "UPDATE auth_sessions" in sql:
            result = _Result(rowcount=2)
        elif "FROM user_accounts ua\n                    ORDER BY ua.created_at DESC" in sql:
            result = _Result(
                mappings_all=[
                    {
                        "id": uuid4(),
                        "email": "admin@example.com",
                        "display_name": "Admin",
                        "account_status": "active",
                        "updated_at": datetime.now(tz=UTC),
                        "is_admin": True,
                    }
                ]
            )
        else:
            result = _Result()
        return result


class _EngineDouble:
    def __init__(self, connection: _ConnectionDouble) -> None:
        self._connection = connection

    @contextmanager
    def begin(self) -> Iterator[_ConnectionDouble]:
        yield self._connection


def test_persisted_repository_methods_cover_foundational_paths() -> None:
    """Exercise all foundational repository methods with a SQL execution double."""
    connection = _ConnectionDouble()
    repository = PersistedAuthManagementRepository(engine=cast(Engine, _EngineDouble(connection)))

    account = repository.create_user_account(
        email="user@example.com",
        password_hash="hash",
        display_name="User",
        is_admin=True,
    )
    by_email = repository.get_user_by_email(email="user@example.com")
    by_id = repository.get_user_by_id(user_id=str(account["user_id"]))
    repository.update_failed_sign_in(
        user_id=str(account["user_id"]),
        failed_sign_in_count=2,
        lockout_until=None,
    )
    repository.update_password_hash(user_id=str(account["user_id"]), password_hash="hash2")
    updated_profile = repository.update_user_profile(
        user_id=str(account["user_id"]),
        display_name="Updated User",
    )
    created_session = repository.create_session(
        user_id=str(account["user_id"]),
        expires_at=datetime.now(tz=UTC).isoformat(),
        client_metadata={"client_label": "Browser"},
    )
    created_session_id = cast(str, created_session["session_id"])
    active_session = repository.get_active_session(session_id=created_session_id)
    sessions = repository.list_active_sessions(user_id=str(account["user_id"]))
    revoked = repository.revoke_session(
        user_id=str(account["user_id"]),
        session_id=created_session_id,
        reason="manual",
    )
    revoked_count = repository.revoke_all_sessions_for_user(
        user_id=str(account["user_id"]),
        reason="all",
    )
    password_revoked_count = repository.change_password_and_revoke_sessions(
        user_id=str(account["user_id"]),
        password_hash="hash3",
        reason="password_changed",
    )
    deletion_pending = repository.request_account_deletion(
        user_id=str(account["user_id"]),
        deletion_due_at=datetime.now(tz=UTC).isoformat(),
    )
    admin_users = repository.list_admin_users()
    repository.write_audit_event(
        event_type="sign_in_success",
        user_id=str(account["user_id"]),
        actor_user_id=str(account["user_id"]),
        event_context={"reason": "test"},
    )

    assert by_email is not None
    assert by_id is not None
    assert updated_profile is not None
    assert active_session is not None
    assert sessions[0]["session_status"] == "active"
    assert revoked is True
    expected_revoked_count = 2
    assert revoked_count == expected_revoked_count
    assert password_revoked_count == expected_revoked_count
    assert deletion_pending is not None
    assert admin_users[0]["is_admin"] is True
    assert len(connection.executed) > 0
