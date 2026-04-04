"""Runtime guard coverage for foundational auth/account HTTP routes."""

# ruff: noqa: D103, E501

from __future__ import annotations

import json
import socket
import sys
import threading
from collections.abc import Iterator
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any, cast
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.errors import ContractQueryError
from src.http_api_server import DatasetApiHandler
from src.query.dataset_discovery_service import DatasetDiscoveryService


class _NoopDiscoveryService:
    pass


class _AuthServiceDouble:
    def __init__(self) -> None:
        self._admin_users = {
            "user-1": {
                "user_id": "user-1",
                "email": "user@example.com",
                "display_name": "User",
                "account_status": "active",
                "is_admin": False,
                "privilege_level": "user",
                "updated_at": "2026-04-02T00:00:00+00:00",
            }
        }

    def authenticate_session(self, *, session_id: str) -> dict[str, object]:
        if session_id == "admin-session":
            return {
                "session_id": session_id,
                "user": {
                    "user_id": "admin-1",
                    "email": "admin@example.com",
                    "display_name": "Admin",
                    "account_status": "active",
                    "is_admin": True,
                    "privilege_level": "admin",
                },
            }
        if session_id == "user-session":
            return {
                "session_id": session_id,
                "user": {
                    "user_id": "user-1",
                    "email": "user@example.com",
                    "display_name": "User",
                    "account_status": "active",
                    "is_admin": False,
                    "privilege_level": "user",
                },
            }
        raise ContractQueryError("auth_required")

    def get_account_navigation(self, *, user_id: str) -> Any:
        class _Response:
            def model_dump(self) -> dict[str, object]:
                return {
                    "account_route": "/settings",
                    "show_admin_entry": False,
                    "admin_route": None,
                    "role_chip": None,
                    "privilege_level": "user",
                }

        return _Response()

    def get_admin_navigation(self, *, user_id: str) -> Any:
        class _Response:
            def model_dump(self) -> dict[str, object]:
                return {
                    "items": [
                        {
                            "item_key": "admin_users",
                            "label": "Users",
                            "route": "/admin/users",
                            "description": "Manage account status, sessions, and admin roles.",
                        }
                    ]
                }

        return _Response()

    def list_user_sessions(self, *, user_id: str) -> Any:
        class _Response:
            def model_dump(self) -> dict[str, object]:
                return {
                    "items": [
                        {
                            "session_id": "session-1",
                            "created_at": "2026-04-02T00:00:00+00:00",
                            "expires_at": "2026-05-02T00:00:00+00:00",
                            "session_status": "active",
                            "client_label": "Browser",
                        }
                    ]
                }

        return _Response()

    def list_admin_users(self) -> Any:
        class _Response:
            def __init__(self, items: list[dict[str, object]]) -> None:
                self._items = items

            def model_dump(self) -> dict[str, object]:
                return {"items": self._items}

        return _Response([dict(item) for item in self._admin_users.values()])

    def update_admin_user_status(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        account_status: str,
    ) -> Any:
        if user_id not in self._admin_users:
            raise ContractQueryError("account_not_found")

        payload = {
            **self._admin_users[user_id],
            "account_status": account_status,
            "updated_at": "2026-04-02T00:10:00+00:00",
        }
        self._admin_users[user_id] = payload

        class _Response:
            def __init__(self, item: dict[str, object]) -> None:
                self._item = item

            def model_dump(self) -> dict[str, object]:
                return self._item

        return _Response(payload)

    def admin_revoke_user_sessions(self, *, actor_user_id: str, user_id: str) -> int:
        if user_id not in self._admin_users:
            raise ContractQueryError("account_not_found")
        return 1

    def register_account(
        self,
        *,
        email: str,
        password: str,
        display_name: str | None,
        client_metadata: dict[str, object] | None,
    ) -> Any:
        class _Response:
            def model_dump(self) -> dict[str, object]:
                return {
                    "user": {
                        "user_id": "user-1",
                        "email": email,
                        "display_name": display_name,
                        "account_status": "active",
                        "is_admin": False,
                        "privilege_level": "user",
                    },
                    "session": {
                        "session_id": "user-session",
                        "created_at": "2026-04-02T00:00:00+00:00",
                        "expires_at": "2026-05-02T00:00:00+00:00",
                        "session_status": "active",
                        "client_label": "Browser",
                    },
                }

        return _Response()

    def login(
        self,
        *,
        email: str,
        password: str,
        client_metadata: dict[str, object] | None,
    ) -> Any:
        return self.register_account(
            email=email,
            password=password,
            display_name="User",
            client_metadata=client_metadata,
        )

    def logout(self, *, user_id: str, session_id: str) -> None:
        return None

    def revoke_user_session(self, *, user_id: str, session_id: str) -> None:
        return None

    def get_account_profile(self, *, user_id: str) -> Any:
        class _Response:
            def model_dump(self) -> dict[str, object]:
                return {
                    "user_id": user_id,
                    "email": "user@example.com",
                    "display_name": "User",
                    "account_status": "active",
                    "is_admin": False,
                    "privilege_level": "user",
                    "updated_at": "2026-04-02T00:00:00+00:00",
                }

        return _Response()

    def update_account_profile(
        self,
        *,
        user_id: str,
        email: str | None,
        display_name: str | None,
    ) -> Any:
        class _Response:
            def model_dump(self) -> dict[str, object]:
                return {
                    "user_id": user_id,
                    "email": email or "user@example.com",
                    "display_name": display_name,
                    "account_status": "active",
                    "is_admin": False,
                    "privilege_level": "user",
                    "updated_at": "2026-04-02T00:10:00+00:00",
                }

        return _Response()

    def update_admin_user_role(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        role_action: str,
    ) -> Any:
        if user_id == "owner-1":
            raise ContractQueryError("owner_role_protected")

        class _Response:
            def model_dump(self) -> dict[str, object]:
                is_admin = role_action == "grant_admin"
                return {
                    "user_id": user_id,
                    "email": "user@example.com",
                    "display_name": "User",
                    "account_status": "active",
                    "is_admin": is_admin,
                    "privilege_level": "admin" if is_admin else "user",
                    "updated_at": "2026-04-02T00:20:00+00:00",
                }

        return _Response()

    def change_account_password(
        self,
        *,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> None:
        return None

    def request_account_deletion(self, *, user_id: str) -> Any:
        class _Response:
            def model_dump(self) -> dict[str, object]:
                return {
                    "user_id": user_id,
                    "account_status": "deletion_pending",
                    "deletion_due_at": "2026-04-09T00:00:00+00:00",
                }

        return _Response()


@pytest.fixture
def auth_guard_http_server() -> Iterator[tuple[str, int]]:
    original_service = DatasetApiHandler.service
    original_auth_service = DatasetApiHandler.auth_service

    DatasetApiHandler.service = cast(DatasetDiscoveryService, _NoopDiscoveryService())
    DatasetApiHandler.auth_service = cast(Any, _AuthServiceDouble())

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    host, port = sock.getsockname()
    sock.close()

    server = ThreadingHTTPServer((host, port), DatasetApiHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield host, port
    finally:
        server.shutdown()
        server.server_close()
        DatasetApiHandler.service = original_service
        DatasetApiHandler.auth_service = original_auth_service


def _request_json(url: str, *, method: str = "GET", token: str | None = None) -> dict[str, Any]:
    request = Request(url=url, method=method)
    if token is not None:
        request.add_header("Authorization", f"Bearer {token}")

    with urlopen(request, timeout=5) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def _request_with_body(
    url: str,
    *,
    method: str,
    payload: dict[str, object],
    token: str | None = None,
) -> tuple[int, dict[str, Any] | None]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(url=url, method=method, data=body)
    request.add_header("Content-Type", "application/json")
    if token is not None:
        request.add_header("Authorization", f"Bearer {token}")

    with urlopen(request, timeout=5) as response:  # noqa: S310
        data = response.read().decode("utf-8")
        return response.status, (json.loads(data) if data else None)


def test_auth_sessions_requires_authenticated_principal(
    auth_guard_http_server: tuple[str, int],
) -> None:
    host, port = auth_guard_http_server

    with pytest.raises(HTTPError) as unauthenticated:
        _request_json(f"http://{host}:{port}/api/auth/sessions")

    assert unauthenticated.value.code == HTTPStatus.UNAUTHORIZED

    payload = _request_json(
        f"http://{host}:{port}/api/auth/sessions",
        token="user-session",
    )
    assert payload["items"][0]["session_id"] == "session-1"


def test_admin_users_requires_admin_principal(auth_guard_http_server: tuple[str, int]) -> None:
    host, port = auth_guard_http_server

    with pytest.raises(HTTPError) as forbidden:
        _request_json(
            f"http://{host}:{port}/api/admin/users",
            token="user-session",
        )

    assert forbidden.value.code == HTTPStatus.FORBIDDEN

    payload = _request_json(
        f"http://{host}:{port}/api/admin/users",
        token="admin-session",
    )
    assert len(payload["items"]) == 1


def test_account_and_admin_navigation_routes_require_proper_authz(
    auth_guard_http_server: tuple[str, int],
) -> None:
    host, port = auth_guard_http_server

    account_navigation = _request_json(
        f"http://{host}:{port}/api/account/navigation",
        token="user-session",
    )
    assert account_navigation["account_route"] == "/settings"

    with pytest.raises(HTTPError) as forbidden:
        _request_json(
            f"http://{host}:{port}/api/admin/navigation",
            token="user-session",
        )
    assert forbidden.value.code == HTTPStatus.FORBIDDEN

    admin_navigation = _request_json(
        f"http://{host}:{port}/api/admin/navigation",
        token="admin-session",
    )
    assert admin_navigation["items"][0]["route"] == "/admin/users"


def test_auth_post_and_patch_routes_cover_guard_and_dispatch_paths(
    auth_guard_http_server: tuple[str, int],
) -> None:
    """Verify foundational auth POST/PATCH branches and guard status codes."""
    host, port = auth_guard_http_server
    register_status, register_payload = _request_with_body(
        f"http://{host}:{port}/api/auth/register",
        method="POST",
        payload={"email": "user@example.com", "password": "verysecure123"},
    )
    assert register_status == HTTPStatus.CREATED
    assert register_payload is not None
    assert register_payload["user"]["email"] == "user@example.com"

    login_status, _login_payload = _request_with_body(
        f"http://{host}:{port}/api/auth/login",
        method="POST",
        payload={"email": "user@example.com", "password": "verysecure123"},
    )
    assert login_status == HTTPStatus.OK

    with pytest.raises(HTTPError) as unauth_logout:
        _request_with_body(
            f"http://{host}:{port}/api/auth/logout",
            method="POST",
            payload={},
        )
    assert unauth_logout.value.code == HTTPStatus.UNAUTHORIZED

    logout_request = Request(f"http://{host}:{port}/api/auth/logout", method="POST")
    logout_request.add_header("Authorization", "Bearer user-session")
    with urlopen(logout_request, timeout=5) as logout_response:  # noqa: S310
        assert logout_response.status == HTTPStatus.NO_CONTENT

    deletion_status, deletion_payload = _request_with_body(
        f"http://{host}:{port}/api/account/deletion-request",
        method="POST",
        payload={},
        token="user-session",
    )
    assert deletion_status == HTTPStatus.ACCEPTED
    assert deletion_payload is not None
    assert deletion_payload["account_status"] == "deletion_pending"

    profile_status, profile_payload = _request_with_body(
        f"http://{host}:{port}/api/account/profile",
        method="PATCH",
        payload={"display_name": "Updated"},
        token="user-session",
    )
    assert profile_status == HTTPStatus.OK
    assert profile_payload is not None
    assert profile_payload["display_name"] == "Updated"

    profile_get_payload = _request_json(
        f"http://{host}:{port}/api/account/profile",
        token="user-session",
    )
    assert profile_get_payload["user_id"] == "user-1"

    admin_status_update, admin_status_payload = _request_with_body(
        f"http://{host}:{port}/api/admin/users/user-1/status",
        method="PATCH",
        payload={"account_status": "active"},
        token="admin-session",
    )
    assert admin_status_update == HTTPStatus.OK
    assert admin_status_payload is not None
    assert admin_status_payload["account_status"] == "active"

    admin_role_update, admin_role_payload = _request_with_body(
        f"http://{host}:{port}/api/admin/users/user-1/role",
        method="PATCH",
        payload={"role_action": "grant_admin"},
        token="admin-session",
    )
    assert admin_role_update == HTTPStatus.OK
    assert admin_role_payload is not None
    assert admin_role_payload["is_admin"] is True

    with pytest.raises(HTTPError) as invalid_role_action:
        _request_with_body(
            f"http://{host}:{port}/api/admin/users/user-1/role",
            method="PATCH",
            payload={"role_action": "invalid"},
            token="admin-session",
        )
    assert invalid_role_action.value.code == HTTPStatus.BAD_REQUEST

    admin_revoke_status, admin_revoke_payload = _request_with_body(
        f"http://{host}:{port}/api/admin/users/user-1/sessions/revoke",
        method="POST",
        payload={},
        token="admin-session",
    )
    assert admin_revoke_status == HTTPStatus.NO_CONTENT
    assert admin_revoke_payload is None

    revoke_request = Request(
        f"http://{host}:{port}/api/auth/sessions/user-session/revoke",
        method="POST",
    )
    revoke_request.add_header("Authorization", "Bearer user-session")
    with urlopen(revoke_request, timeout=5) as revoke_response:  # noqa: S310
        assert revoke_response.status == HTTPStatus.NO_CONTENT

    with pytest.raises(HTTPError) as invalid_status:
        _request_with_body(
            f"http://{host}:{port}/api/admin/users/user-1/status",
            method="PATCH",
            payload={"account_status": "paused"},
            token="admin-session",
        )
    assert invalid_status.value.code == HTTPStatus.BAD_REQUEST

    with pytest.raises(HTTPError) as unknown_route:
        _request_with_body(
            f"http://{host}:{port}/api/auth/unknown",
            method="POST",
            payload={},
        )
    assert unknown_route.value.code == HTTPStatus.NOT_FOUND


def test_post_and_patch_return_500_when_auth_service_missing() -> None:
    """Auth endpoints should fail fast when auth service is not initialized."""
    original_service = DatasetApiHandler.service
    original_auth_service = DatasetApiHandler.auth_service
    DatasetApiHandler.service = cast(DatasetDiscoveryService, _NoopDiscoveryService())
    DatasetApiHandler.auth_service = None

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    host, port = sock.getsockname()
    sock.close()

    server = ThreadingHTTPServer((host, port), DatasetApiHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with pytest.raises(HTTPError) as post_error:
            _request_with_body(
                f"http://{host}:{port}/api/auth/register",
                method="POST",
                payload={"email": "user@example.com", "password": "verysecure123"},
            )
        assert post_error.value.code == HTTPStatus.INTERNAL_SERVER_ERROR

        with pytest.raises(HTTPError) as patch_error:
            _request_with_body(
                f"http://{host}:{port}/api/account/profile",
                method="PATCH",
                payload={"display_name": "User"},
            )
        assert patch_error.value.code == HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        server.shutdown()
        server.server_close()
        DatasetApiHandler.service = original_service
        DatasetApiHandler.auth_service = original_auth_service
