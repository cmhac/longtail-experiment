"""Contract coverage for admin user-management HTTP endpoints."""

# ruff: noqa: D103

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

_EXPECTED_ADMIN_USER_COUNT = 2


class _NoopDiscoveryService:
    pass


class _AuthServiceDouble:
    def __init__(self) -> None:
        self.admin_users = {
            "admin-1": {
                "user_id": "admin-1",
                "email": "admin@example.com",
                "display_name": "Admin",
                "account_status": "active",
                "is_admin": True,
                "updated_at": "2026-04-03T00:00:00+00:00",
            },
            "user-1": {
                "user_id": "user-1",
                "email": "user@example.com",
                "display_name": "User",
                "account_status": "active",
                "is_admin": False,
                "updated_at": "2026-04-03T00:00:00+00:00",
            },
        }

    def authenticate_session(self, *, session_id: str) -> dict[str, object]:
        if session_id == "admin-session":
            return {
                "session_id": "admin-session",
                "user": {
                    "user_id": "admin-1",
                    "email": "admin@example.com",
                    "display_name": "Admin",
                    "account_status": "active",
                    "is_admin": True,
                },
            }
        if session_id == "user-session":
            return {
                "session_id": "user-session",
                "user": {
                    "user_id": "user-1",
                    "email": "user@example.com",
                    "display_name": "User",
                    "account_status": "active",
                    "is_admin": False,
                },
            }
        raise ContractQueryError("auth_required")

    def list_admin_users(self) -> Any:
        class _Response:
            def __init__(self, items: list[dict[str, object]]) -> None:
                self._items = items

            def model_dump(self) -> dict[str, object]:
                return {"items": self._items}

        return _Response([dict(item) for item in self.admin_users.values()])

    def update_admin_user_status(
        self,
        *,
        actor_user_id: str,
        user_id: str,
        account_status: str,
    ) -> Any:
        if user_id not in self.admin_users:
            raise ContractQueryError("account_not_found")
        if user_id == "admin-1" and account_status == "deactivated":
            raise ContractQueryError("final_admin_guard")

        self.admin_users[user_id] = {
            **self.admin_users[user_id],
            "account_status": account_status,
            "updated_at": "2026-04-03T00:10:00+00:00",
        }

        class _Response:
            def __init__(self, payload: dict[str, object]) -> None:
                self._payload = payload

            def model_dump(self) -> dict[str, object]:
                return self._payload

        return _Response(dict(self.admin_users[user_id]))

    def admin_revoke_user_sessions(self, *, actor_user_id: str, user_id: str) -> int:
        if user_id not in self.admin_users:
            raise ContractQueryError("account_not_found")
        return 2


@pytest.fixture
def admin_contract_http_server() -> Iterator[tuple[str, int]]:
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


def _request(
    url: str,
    *,
    method: str,
    payload: dict[str, object] | None = None,
    token: str | None = None,
) -> tuple[int, dict[str, Any] | None]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(url=url, method=method, data=body)
    request.add_header("Content-Type", "application/json")
    if token is not None:
        request.add_header("Authorization", f"Bearer {token}")

    with urlopen(request, timeout=5) as response:  # noqa: S310
        raw = response.read().decode("utf-8")
        return response.status, (json.loads(raw) if raw else None)


def test_admin_user_list_requires_admin_and_returns_users(
    admin_contract_http_server: tuple[str, int],
) -> None:
    host, port = admin_contract_http_server

    with pytest.raises(HTTPError) as forbidden:
        _request(f"http://{host}:{port}/api/admin/users", method="GET", token="user-session")
    assert forbidden.value.code == HTTPStatus.FORBIDDEN

    status, payload = _request(
        f"http://{host}:{port}/api/admin/users",
        method="GET",
        token="admin-session",
    )
    assert status == HTTPStatus.OK
    assert payload is not None
    assert len(payload["items"]) == _EXPECTED_ADMIN_USER_COUNT


def test_admin_status_update_endpoint_contract(admin_contract_http_server: tuple[str, int]) -> None:
    host, port = admin_contract_http_server

    status, payload = _request(
        f"http://{host}:{port}/api/admin/users/user-1/status",
        method="PATCH",
        payload={"account_status": "deactivated"},
        token="admin-session",
    )
    assert status == HTTPStatus.OK
    assert payload is not None
    assert payload["account_status"] == "deactivated"

    with pytest.raises(HTTPError) as final_admin_conflict:
        _request(
            f"http://{host}:{port}/api/admin/users/admin-1/status",
            method="PATCH",
            payload={"account_status": "deactivated"},
            token="admin-session",
        )
    assert final_admin_conflict.value.code == HTTPStatus.CONFLICT


def test_admin_session_revoke_endpoint_contract(
    admin_contract_http_server: tuple[str, int],
) -> None:
    host, port = admin_contract_http_server

    status, payload = _request(
        f"http://{host}:{port}/api/admin/users/user-1/sessions/revoke",
        method="POST",
        payload={},
        token="admin-session",
    )
    assert status == HTTPStatus.NO_CONTENT
    assert payload is None

    with pytest.raises(HTTPError) as forbidden:
        _request(
            f"http://{host}:{port}/api/admin/users/user-1/sessions/revoke",
            method="POST",
            payload={},
            token="user-session",
        )
    assert forbidden.value.code == HTTPStatus.FORBIDDEN
