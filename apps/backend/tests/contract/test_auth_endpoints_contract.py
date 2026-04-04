"""Contract coverage for auth register/login/logout HTTP endpoints."""

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


class _NoopDiscoveryService:
    pass


class _AuthServiceDouble:
    def authenticate_session(self, *, session_id: str) -> dict[str, object]:
        if session_id == "valid-session":
            return {
                "session_id": "valid-session",
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

    def register_account(
        self,
        *,
        email: str,
        password: str,
        display_name: str | None,
        client_metadata: dict[str, object] | None,
    ) -> Any:
        if email == "duplicate@example.com":
            raise ContractQueryError("duplicate_email")

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
                        "session_id": "valid-session",
                        "created_at": "2026-04-02T00:00:00+00:00",
                        "expires_at": "2026-05-02T00:00:00+00:00",
                        "session_status": "active",
                        "client_label": (
                            str(client_metadata.get("client_label"))
                            if isinstance(client_metadata, dict)
                            else None
                        ),
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
        if email == "locked@example.com":
            raise ContractQueryError("account_locked")
        if password == "wrong-password":
            raise ContractQueryError("invalid_credentials")

        return self.register_account(
            email=email,
            password=password,
            display_name="User",
            client_metadata=client_metadata,
        )

    def logout(self, *, user_id: str, session_id: str) -> None:
        if session_id != "valid-session":
            raise ContractQueryError("session_not_found")

    def revoke_user_session(self, *, user_id: str, session_id: str) -> None:
        if session_id != "revokable-session":
            raise ContractQueryError("session_not_found")


@pytest.fixture
def auth_contract_http_server() -> Iterator[tuple[str, int]]:
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


def test_register_endpoint_contract(auth_contract_http_server: tuple[str, int]) -> None:
    host, port = auth_contract_http_server

    status, payload = _request(
        f"http://{host}:{port}/api/auth/register",
        method="POST",
        payload={
            "email": "user@example.com",
            "password": "verysecure123",
            "display_name": "User",
        },
    )

    assert status == HTTPStatus.CREATED
    assert payload is not None
    assert payload["user"]["email"] == "user@example.com"
    assert payload["session"]["session_status"] == "active"


def test_login_endpoint_contract_and_error_statuses(
    auth_contract_http_server: tuple[str, int],
) -> None:
    host, port = auth_contract_http_server

    status, payload = _request(
        f"http://{host}:{port}/api/auth/login",
        method="POST",
        payload={"email": "user@example.com", "password": "verysecure123"},
    )
    assert status == HTTPStatus.OK
    assert payload is not None
    assert payload["session"]["session_id"] == "valid-session"

    with pytest.raises(HTTPError) as invalid:
        _request(
            f"http://{host}:{port}/api/auth/login",
            method="POST",
            payload={"email": "user@example.com", "password": "wrong-password"},
        )
    assert invalid.value.code == HTTPStatus.UNAUTHORIZED

    with pytest.raises(HTTPError) as locked:
        _request(
            f"http://{host}:{port}/api/auth/login",
            method="POST",
            payload={"email": "locked@example.com", "password": "verysecure123"},
        )
    assert locked.value.code == HTTPStatus.LOCKED


def test_logout_endpoint_contract(auth_contract_http_server: tuple[str, int]) -> None:
    host, port = auth_contract_http_server

    with pytest.raises(HTTPError) as unauthenticated:
        _request(
            f"http://{host}:{port}/api/auth/logout",
            method="POST",
            payload={},
        )
    assert unauthenticated.value.code == HTTPStatus.UNAUTHORIZED

    request = Request(f"http://{host}:{port}/api/auth/logout", method="POST")
    request.add_header("Authorization", "Bearer valid-session")
    with urlopen(request, timeout=5) as response:  # noqa: S310
        assert response.status == HTTPStatus.NO_CONTENT


def test_unified_auth_sessions_endpoint_actions(auth_contract_http_server: tuple[str, int]) -> None:
    host, port = auth_contract_http_server

    register_status, register_payload = _request(
        f"http://{host}:{port}/api/auth/sessions",
        method="POST",
        payload={
            "action": "register",
            "email": "unified-register@example.com",
            "password": "verysecure123",
            "display_name": "Unified User",
        },
    )
    assert register_status == HTTPStatus.CREATED
    assert register_payload is not None
    assert register_payload["user"]["email"] == "unified-register@example.com"

    login_status, login_payload = _request(
        f"http://{host}:{port}/api/auth/sessions",
        method="POST",
        payload={
            "action": "login",
            "email": "user@example.com",
            "password": "verysecure123",
        },
    )
    assert login_status == HTTPStatus.OK
    assert login_payload is not None
    assert login_payload["session"]["session_id"] == "valid-session"

    revoke_status, revoke_payload = _request(
        f"http://{host}:{port}/api/auth/sessions",
        method="POST",
        payload={"action": "revoke", "session_id": "revokable-session"},
        token="valid-session",
    )
    assert revoke_status == HTTPStatus.NO_CONTENT
    assert revoke_payload is None

    logout_status, logout_payload = _request(
        f"http://{host}:{port}/api/auth/sessions",
        method="POST",
        payload={"action": "logout"},
        token="valid-session",
    )
    assert logout_status == HTTPStatus.NO_CONTENT
    assert logout_payload is None

    with pytest.raises(HTTPError) as invalid_action:
        _request(
            f"http://{host}:{port}/api/auth/sessions",
            method="POST",
            payload={"action": "invalid"},
        )
    assert invalid_action.value.code == HTTPStatus.BAD_REQUEST

    with pytest.raises(HTTPError) as missing_revoke_session:
        _request(
            f"http://{host}:{port}/api/auth/sessions",
            method="POST",
            payload={"action": "revoke"},
            token="valid-session",
        )
    assert missing_revoke_session.value.code == HTTPStatus.BAD_REQUEST
