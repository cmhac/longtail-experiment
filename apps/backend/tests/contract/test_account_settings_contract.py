"""Contract coverage for account settings profile and password endpoints."""

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

_MIN_PASSWORD_LENGTH = 12


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
                },
            }
        raise ContractQueryError("auth_required")

    def get_account_profile(self, *, user_id: str) -> Any:
        class _Response:
            def model_dump(self) -> dict[str, object]:
                return {
                    "user_id": user_id,
                    "email": "user@example.com",
                    "display_name": "User",
                    "account_status": "active",
                    "is_admin": False,
                    "updated_at": "2026-04-03T00:00:00+00:00",
                }

        return _Response()

    def update_account_profile(self, *, user_id: str, display_name: str | None) -> Any:
        class _Response:
            def model_dump(self) -> dict[str, object]:
                return {
                    "user_id": user_id,
                    "email": "user@example.com",
                    "display_name": display_name,
                    "account_status": "active",
                    "is_admin": False,
                    "updated_at": "2026-04-03T00:10:00+00:00",
                }

        return _Response()

    def change_account_password(
        self,
        *,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> None:
        if current_password != "oldpassword123":
            raise ContractQueryError("invalid_credentials")
        if len(new_password) < _MIN_PASSWORD_LENGTH:
            raise ContractQueryError("password must be at least 12 characters")

    def request_account_deletion(self, *, user_id: str) -> Any:
        class _Response:
            def model_dump(self) -> dict[str, object]:
                return {
                    "user_id": user_id,
                    "account_status": "deletion_pending",
                    "deletion_due_at": "2026-04-10T00:00:00+00:00",
                }

        return _Response()


@pytest.fixture
def account_settings_contract_http_server() -> Iterator[tuple[str, int]]:
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


def test_account_profile_endpoints_contract(
    account_settings_contract_http_server: tuple[str, int],
) -> None:
    host, port = account_settings_contract_http_server

    with pytest.raises(HTTPError) as unauthenticated:
        _request(f"http://{host}:{port}/api/account/profile", method="GET")
    assert unauthenticated.value.code == HTTPStatus.UNAUTHORIZED

    status, payload = _request(
        f"http://{host}:{port}/api/account/profile",
        method="GET",
        token="valid-session",
    )
    assert status == HTTPStatus.OK
    assert payload is not None
    assert payload["email"] == "user@example.com"

    patch_status, patch_payload = _request(
        f"http://{host}:{port}/api/account/profile",
        method="PATCH",
        payload={"display_name": "Updated User"},
        token="valid-session",
    )
    assert patch_status == HTTPStatus.OK
    assert patch_payload is not None
    assert patch_payload["display_name"] == "Updated User"


def test_account_password_endpoint_contract(
    account_settings_contract_http_server: tuple[str, int],
) -> None:
    host, port = account_settings_contract_http_server

    status, payload = _request(
        f"http://{host}:{port}/api/account/password",
        method="POST",
        payload={
            "current_password": "oldpassword123",
            "new_password": "newpassword123",
        },
        token="valid-session",
    )
    assert status == HTTPStatus.NO_CONTENT
    assert payload is None

    with pytest.raises(HTTPError) as bad_password:
        _request(
            f"http://{host}:{port}/api/account/password",
            method="POST",
            payload={
                "current_password": "wrong-password",
                "new_password": "newpassword123",
            },
            token="valid-session",
        )
    assert bad_password.value.code == HTTPStatus.UNAUTHORIZED


def test_deletion_request_endpoint_contract(
    account_settings_contract_http_server: tuple[str, int],
) -> None:
    host, port = account_settings_contract_http_server

    status, payload = _request(
        f"http://{host}:{port}/api/account/deletion-request",
        method="POST",
        token="valid-session",
    )
    assert status == HTTPStatus.ACCEPTED
    assert payload is not None
    assert payload["account_status"] == "deletion_pending"
