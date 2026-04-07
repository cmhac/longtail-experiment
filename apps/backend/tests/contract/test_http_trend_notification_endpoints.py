"""Contract coverage for trend notification HTTP endpoints."""

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
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4

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
        if session_id == "deactivated-session":
            raise ContractQueryError("auth_required")
        raise ContractQueryError("auth_required")


class _NotificationServiceDouble:
    def __init__(self) -> None:
        notification_id = str(uuid4())
        self.list_payload = {
            "items": [
                {
                    "notification_id": notification_id,
                    "event_id": str(uuid4()),
                    "dataset_id": "PRICE.US.CPI",
                    "title": "Trend reversal detected",
                    "body": "PRICE.US.CPI: up to down",
                    "previous_direction": "up",
                    "current_direction": "down",
                    "confidence_score": 0.74,
                    "effective_observed_on": "2026-01-01",
                    "destination_path": "/datasets/PRICE.US.CPI",
                    "unread": True,
                    "read_at": None,
                    "delivered_at": "2026-01-02T00:00:00+00:00",
                    "channel": "in_app",
                    "delivery_status": "delivered",
                    "processing_context": "incremental",
                    "visibility_classification": "user_visible",
                }
            ],
            "pagination": {
                "page_size": 25,
                "has_more": False,
                "next_cursor": None,
            },
        }
        self.summary_payload = {
            "unread_count": 1,
            "last_notification_at": "2026-01-02T00:00:00+00:00",
            "generated_at": "2026-01-02T00:00:01+00:00",
        }
        self.subscription_payload = {
            "items": [
                {
                    "dataset_id": "PRICE.US.CPI",
                    "subscribed_at": "2026-01-02T00:00:00+00:00",
                    "unsubscribed_at": None,
                }
            ]
        }

    def list_notifications(
        self,
        *,
        user_id: str,
        page_size: int | None,
        cursor: str | None,
        unread_only: bool,
    ) -> Any:
        del user_id, cursor, unread_only
        if page_size is not None and page_size < 1:
            raise ContractQueryError("page_size must be between 1 and 100")

        class _Response:
            def model_dump(self_inner) -> dict[str, object]:
                return {
                    **self.list_payload,
                    "pagination": {
                        **cast(dict[str, object], self.list_payload["pagination"]),
                        "page_size": page_size or 25,
                    },
                }

        return _Response()

    def get_unread_summary(self, *, user_id: str) -> Any:
        del user_id

        class _Response:
            def model_dump(self_inner) -> dict[str, object]:
                return dict(self.summary_payload)

        return _Response()

    def mark_notification_read(self, *, user_id: str, notification_id: str) -> Any:
        del user_id
        if notification_id == "missing":
            raise ContractQueryError("notification_not_found")

        class _Response:
            def model_dump(self_inner) -> dict[str, object]:
                return {
                    "notification_id": notification_id,
                    "updated": True,
                    "unread_count": 0,
                }

        return _Response()

    def mark_notification_unread(self, *, user_id: str, notification_id: str) -> Any:
        del user_id
        if notification_id == "missing":
            raise ContractQueryError("notification_not_found")

        class _Response:
            def model_dump(self_inner) -> dict[str, object]:
                return {
                    "notification_id": notification_id,
                    "updated": True,
                    "unread_count": 1,
                }

        return _Response()

    def mark_all_notifications_read(self, *, user_id: str) -> Any:
        del user_id

        class _Response:
            def model_dump(self_inner) -> dict[str, object]:
                return {
                    "updated_count": 1,
                    "unread_count": 0,
                }

        return _Response()

    def list_subscriptions(self, *, user_id: str) -> Any:
        del user_id

        class _Response:
            def model_dump(self_inner) -> dict[str, object]:
                return dict(self.subscription_payload)

        return _Response()

    def create_subscription(self, *, user_id: str, dataset_id: str) -> Any:
        del user_id
        if dataset_id == "UNKNOWN":
            raise ContractQueryError("dataset_not_found")

        class _Response:
            def model_dump(self_inner) -> dict[str, object]:
                return {
                    "dataset_id": dataset_id,
                    "subscribed_at": "2026-01-02T00:00:00+00:00",
                    "created": True,
                }

        return _Response()

    def delete_subscription(self, *, user_id: str, dataset_id: str) -> Any:
        del user_id

        class _Response:
            def model_dump(self_inner) -> dict[str, object]:
                return {
                    "dataset_id": dataset_id,
                    "removed": True,
                }

        return _Response()


@pytest.fixture
def notification_contract_http_server() -> Iterator[tuple[str, int]]:
    original_service = DatasetApiHandler.service
    original_auth_service = DatasetApiHandler.auth_service
    original_notification_service = DatasetApiHandler.notification_service
    DatasetApiHandler.service = cast(DatasetDiscoveryService, _NoopDiscoveryService())
    DatasetApiHandler.auth_service = cast(Any, _AuthServiceDouble())
    DatasetApiHandler.notification_service = cast(Any, _NotificationServiceDouble())

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
        DatasetApiHandler.notification_service = original_notification_service


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


def test_notification_endpoints_require_auth(
    notification_contract_http_server: tuple[str, int],
) -> None:
    host, port = notification_contract_http_server

    with pytest.raises(HTTPError) as unauthenticated:
        _request(f"http://{host}:{port}/api/notifications", method="GET")
    assert unauthenticated.value.code == HTTPStatus.UNAUTHORIZED


def test_notification_list_and_summary_endpoints(
    notification_contract_http_server: tuple[str, int],
) -> None:
    host, port = notification_contract_http_server

    query = urlencode({"page_size": "25", "unread_only": "false"})
    list_status, list_payload = _request(
        f"http://{host}:{port}/api/notifications?{query}",
        method="GET",
        token="valid-session",
    )
    summary_status, summary_payload = _request(
        f"http://{host}:{port}/api/notifications/summary",
        method="GET",
        token="valid-session",
    )

    assert list_status == HTTPStatus.OK
    assert list_payload is not None
    assert list_payload["items"][0]["dataset_id"] == "PRICE.US.CPI"
    assert summary_status == HTTPStatus.OK
    assert summary_payload is not None
    assert summary_payload["unread_count"] == 1


def test_notification_read_mutation_endpoints(
    notification_contract_http_server: tuple[str, int],
) -> None:
    host, port = notification_contract_http_server

    read_status, read_payload = _request(
        f"http://{host}:{port}/api/notifications/{uuid4()}/mark-read",
        method="POST",
        token="valid-session",
    )
    unread_status, unread_payload = _request(
        f"http://{host}:{port}/api/notifications/{uuid4()}/mark-unread",
        method="POST",
        token="valid-session",
    )
    mark_all_status, mark_all_payload = _request(
        f"http://{host}:{port}/api/notifications/mark-all-read",
        method="POST",
        token="valid-session",
    )

    assert read_status == HTTPStatus.OK
    assert read_payload is not None
    assert read_payload["updated"] is True
    assert unread_status == HTTPStatus.OK
    assert unread_payload is not None
    assert unread_payload["updated"] is True
    assert mark_all_status == HTTPStatus.OK
    assert mark_all_payload is not None
    assert mark_all_payload["updated_count"] == 1


def test_notification_not_found_and_bad_request_contracts(
    notification_contract_http_server: tuple[str, int],
) -> None:
    host, port = notification_contract_http_server

    with pytest.raises(HTTPError) as not_found:
        _request(
            f"http://{host}:{port}/api/notifications/missing/mark-read",
            method="POST",
            token="valid-session",
        )
    assert not_found.value.code == HTTPStatus.NOT_FOUND

    with pytest.raises(HTTPError) as bad_request:
        _request(
            f"http://{host}:{port}/api/notifications?page_size=0",
            method="GET",
            token="valid-session",
        )
    assert bad_request.value.code == HTTPStatus.BAD_REQUEST


def test_notification_subscription_endpoints_and_self_only_access(
    notification_contract_http_server: tuple[str, int],
) -> None:
    host, port = notification_contract_http_server

    list_status, list_payload = _request(
        f"http://{host}:{port}/api/notifications/subscriptions",
        method="GET",
        token="valid-session",
    )
    create_status, create_payload = _request(
        f"http://{host}:{port}/api/notifications/subscriptions",
        method="POST",
        payload={"dataset_id": "PRICE.US.CPI"},
        token="valid-session",
    )
    delete_status, delete_payload = _request(
        f"http://{host}:{port}/api/notifications/subscriptions/PRICE.US.CPI",
        method="DELETE",
        token="valid-session",
    )

    assert list_status == HTTPStatus.OK
    assert list_payload is not None
    assert list_payload["items"][0]["dataset_id"] == "PRICE.US.CPI"
    assert create_status == HTTPStatus.OK
    assert create_payload is not None
    assert create_payload["dataset_id"] == "PRICE.US.CPI"
    assert delete_status == HTTPStatus.OK
    assert delete_payload is not None
    assert delete_payload["removed"] is True

    with pytest.raises(HTTPError) as unauthenticated:
        _request(
            f"http://{host}:{port}/api/notifications/subscriptions",
            method="GET",
        )
    assert unauthenticated.value.code == HTTPStatus.UNAUTHORIZED


def test_deactivated_user_access_is_denied(
    notification_contract_http_server: tuple[str, int],
) -> None:
    host, port = notification_contract_http_server

    with pytest.raises(HTTPError) as denied:
        _request(
            f"http://{host}:{port}/api/notifications/summary",
            method="GET",
            token="deactivated-session",
        )
    assert denied.value.code == HTTPStatus.UNAUTHORIZED

    with pytest.raises(HTTPError) as denied_create:
        _request(
            f"http://{host}:{port}/api/notifications/subscriptions",
            method="POST",
            payload={"dataset_id": "PRICE.US.CPI"},
            token="deactivated-session",
        )
    assert denied_create.value.code == HTTPStatus.UNAUTHORIZED
