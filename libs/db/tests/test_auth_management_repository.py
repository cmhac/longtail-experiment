"""Unit tests for postgres auth management repository behavior."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
import sys
from pathlib import Path
from typing import cast
from uuid import UUID, uuid4

from sqlalchemy import Engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from db.repositories.auth_management_repository import PostgresAuthManagementRepository


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

    def scalar_one(self) -> object:
        return self._scalar_one_or_none


class _ConnectionDouble:
    def __init__(self) -> None:
        now = datetime.now(tz=UTC)
        self.executed: list[tuple[str, dict[str, object] | None]] = []
        self.user_row: dict[str, object] | None = {
            "id": uuid4(),
            "email": "user@example.com",
            "email_normalized": "user@example.com",
            "display_name": "User",
            "account_status": "active",
            "privilege_level": "user",
            "failed_sign_in_count": 0,
            "lockout_until": None,
            "updated_at": now,
            "password_hash": "hash",
            "is_admin": False,
        }
        self.active_session_row: dict[str, object] | None = {
            "id": uuid4(),
            "user_id": uuid4(),
            "session_status": "active",
            "created_at": now,
            "expires_at": now,
            "client_metadata": '{"client_label":"Browser"}',
            "email": "user@example.com",
            "display_name": "User",
            "account_status": "active",
            "privilege_level": "owner",
            "is_admin": False,
        }
        self.list_sessions_rows: list[dict[str, object]] = [
            {
                "id": uuid4(),
                "created_at": now,
                "expires_at": now,
                "session_status": "active",
                "client_metadata": {"client_label": "Browser"},
            },
            {
                "id": uuid4(),
                "created_at": now,
                "expires_at": now,
                "session_status": "active",
                "client_metadata": None,
            },
        ]
        self.list_admin_rows: list[dict[str, object]] = [
            {
                "id": uuid4(),
                "email": "admin@example.com",
                "display_name": "Admin",
                "account_status": "active",
                "privilege_level": "admin",
                "updated_at": now,
                "is_admin": True,
            }
        ]
        self.status_target_row: dict[str, object] | None = {
            "id": uuid4(),
            "account_status": "active",
            "is_admin": False,
        }
        self.remaining_admins: int = 1
        self.role_target_row: dict[str, object] | None = {
            "id": uuid4(),
            "privilege_level": "user",
        }
        self.revoke_returning_id: object = uuid4()
        self.update_rowcount: int = 2

    def execute(
        self, statement: object, params: dict[str, object] | None = None
    ) -> _Result:
        sql = str(statement)
        self.executed.append((sql, params))

        if "SELECT id, privilege_level" in sql:
            return _Result(mappings_first=self.role_target_row)
        if "SELECT COUNT(*)" in sql and "role_assignments" in sql:
            return _Result(scalar_one_or_none=self.remaining_admins)
        if "FROM auth_sessions s" in sql:
            return _Result(mappings_first=self.active_session_row)
        if "FROM auth_sessions" in sql and "ORDER BY created_at DESC" in sql:
            return _Result(mappings_all=self.list_sessions_rows)
        if "UPDATE auth_sessions" in sql and "RETURNING id" in sql:
            return _Result(scalar_one_or_none=self.revoke_returning_id)
        if "UPDATE auth_sessions" in sql:
            return _Result(rowcount=self.update_rowcount)
        if "FROM user_accounts ua" in sql and "ORDER BY ua.created_at DESC" in sql:
            return _Result(mappings_all=self.list_admin_rows)
        if "WHERE ua.email_normalized" in sql or (
            "WHERE ua.id = :user_id" in sql and "LEFT JOIN credential_records" in sql
        ):
            return _Result(mappings_first=self.user_row)
        if "ua.account_status" in sql and "WHERE ua.id = :user_id" in sql:
            return _Result(mappings_first=self.status_target_row)
        return _Result()


class _EngineDouble:
    def __init__(self, connection: _ConnectionDouble) -> None:
        self._connection = connection

    @contextmanager
    def begin(self) -> Iterator[_ConnectionDouble]:
        yield self._connection


def _repo(connection: _ConnectionDouble) -> PostgresAuthManagementRepository:
    return PostgresAuthManagementRepository(
        database_url="postgresql+psycopg://ignored",
        engine=cast(Engine, _EngineDouble(connection)),
    )


def test_repository_covers_foundational_paths() -> None:
    connection = _ConnectionDouble()
    repository = _repo(connection)

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
        lockout_until=datetime.now(tz=UTC).isoformat(),
    )
    repository.update_password_hash(
        user_id=str(account["user_id"]), password_hash="hash2"
    )
    updated_profile = repository.update_user_profile(
        user_id=str(account["user_id"]),
        email="next@example.com",
        display_name="Updated User",
    )
    created_session = repository.create_session(
        user_id=str(account["user_id"]),
        expires_at=datetime.now(tz=UTC).isoformat(),
        client_metadata={"client_label": "Browser"},
    )
    session_id = cast(str, created_session["session_id"])
    active_session = repository.get_active_session(session_id=session_id)
    sessions = repository.list_active_sessions(user_id=str(account["user_id"]))
    revoked = repository.revoke_session(
        user_id=str(account["user_id"]),
        session_id=session_id,
        reason="manual",
    )
    revoked_count = repository.revoke_all_sessions_for_user(
        user_id=str(account["user_id"]),
        reason="all",
    )
    admin_users = repository.list_admin_users()
    updated_admin_user, admin_revoked_count = repository.update_admin_user_status(
        actor_user_id=str(account["user_id"]),
        user_id=str(account["user_id"]),
        account_status="deactivated",
    )
    granted_role_user = repository.update_admin_user_role(
        actor_user_id=str(account["user_id"]),
        user_id=str(account["user_id"]),
        role_action="grant_admin",
    )
    revoked_role_user = repository.update_admin_user_role(
        actor_user_id=str(account["user_id"]),
        user_id=str(account["user_id"]),
        role_action="revoke_admin",
    )
    admin_session_revoked_count = repository.revoke_all_sessions_for_user_as_admin(
        user_id=str(account["user_id"]),
        reason="admin_revoke",
    )
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
    session_payload = active_session
    assert session_payload["client_metadata"] == {"client_label": "Browser"}
    session_user = cast(dict[str, object], session_payload["user"])
    assert session_user["is_admin"] is True
    assert sessions[0]["client_label"] == "Browser"
    assert sessions[1]["client_label"] is None
    assert revoked is True
    assert revoked_count == 2
    assert admin_users[0]["is_admin"] is True
    assert updated_admin_user is not None
    assert granted_role_user is not None
    assert revoked_role_user is not None
    assert admin_revoked_count == 2
    assert admin_session_revoked_count == 2
    assert any(
        "account_status = CAST(:account_status AS VARCHAR)" in sql
        for sql, _ in connection.executed
    )


def test_repository_handles_missing_rows_and_false_revoke() -> None:
    connection = _ConnectionDouble()
    connection.user_row = None
    connection.active_session_row = None
    connection.status_target_row = None
    connection.role_target_row = None
    connection.revoke_returning_id = None
    repository = _repo(connection)

    assert repository.get_user_by_email(email="missing@example.com") is None
    assert repository.get_user_by_id(user_id=str(uuid4())) is None
    assert repository.get_active_session(session_id=str(uuid4())) is None
    assert (
        repository.revoke_session(
            user_id=str(uuid4()),
            session_id=str(uuid4()),
            reason="missing",
        )
        is False
    )
    updated, revoked_count = repository.update_admin_user_status(
        actor_user_id=str(uuid4()),
        user_id=str(uuid4()),
        account_status="active",
    )
    assert updated is None
    assert revoked_count == 0
    assert (
        repository.update_admin_user_role(
            actor_user_id=str(uuid4()),
            user_id=str(uuid4()),
            role_action="grant_admin",
        )
        is None
    )


def test_update_admin_user_status_raises_final_admin_guard() -> None:
    connection = _ConnectionDouble()
    connection.status_target_row = {
        "id": uuid4(),
        "account_status": "active",
        "is_admin": True,
    }
    connection.remaining_admins = 0
    repository = _repo(connection)

    try:
        repository.update_admin_user_status(
            actor_user_id=str(uuid4()),
            user_id=str(uuid4()),
            account_status="deactivated",
        )
    except ValueError as exc:
        assert str(exc) == "final_admin_guard"
    else:
        raise AssertionError("Expected final_admin_guard")


def test_update_admin_user_role_enforces_owner_and_invalid_action() -> None:
    connection = _ConnectionDouble()
    repository = _repo(connection)

    connection.role_target_row = {"id": UUID(int=1), "privilege_level": "owner"}
    try:
        repository.update_admin_user_role(
            actor_user_id=str(uuid4()),
            user_id=str(uuid4()),
            role_action="grant_admin",
        )
    except ValueError as exc:
        assert str(exc) == "owner_role_protected"
    else:
        raise AssertionError("Expected owner_role_protected")

    connection.role_target_row = {"id": UUID(int=2), "privilege_level": "user"}
    try:
        repository.update_admin_user_role(
            actor_user_id=str(uuid4()),
            user_id=str(uuid4()),
            role_action="unknown",
        )
    except ValueError as exc:
        assert "role_action must be grant_admin or revoke_admin" in str(exc)
    else:
        raise AssertionError("Expected invalid role_action error")


def test_serialize_user_row_covers_fallback_branches() -> None:
    serialized = PostgresAuthManagementRepository._serialize_user_row(
        {
            "id": uuid4(),
            "email": "user@example.com",
            "email_normalized": "user@example.com",
            "display_name": "User",
            "account_status": "active",
            "failed_sign_in_count": "3",
            "lockout_until": "not-a-datetime",
            "updated_at": "not-a-datetime",
            "password_hash": "hash",
            "is_admin": False,
            "privilege_level": "admin",
        }
    )

    assert serialized["failed_sign_in_count"] == 3
    assert serialized["lockout_until"] is None
    assert serialized["is_admin"] is True
