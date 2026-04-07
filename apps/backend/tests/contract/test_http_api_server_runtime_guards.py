"""Focused coverage for HTTP API server helper and guard branches."""

# ruff: noqa: D103, E501, PLR2004, PLC0415, PLW0108

from __future__ import annotations

import json
import os
import socket
import sys
import threading
from argparse import Namespace
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.errors import ContractQueryError
from src.http_api_server import (
    DatasetApiHandler,
    _env_value,
    _make_service,
    _require_schema_readiness,
    _resolve_expected_revision,
    main,
)
from src.query.dataset_discovery_service import DatasetDiscoveryService


class _ServiceForErrorPaths:
    def search_datasets(self, **_: object) -> tuple[list[dict[str, Any]], int]:
        raise ContractQueryError("invalid_page")

    def list_recent_updates(self, **_: object) -> list[dict[str, Any]]:
        raise ValueError("bad_limit")

    def list_catalog(self, **_: object) -> dict[str, Any]:
        raise ContractQueryError("invalid_source")

    def get_dataset_detail(self, **_: object) -> dict[str, Any]:
        raise ContractQueryError("dataset_not_found")


@pytest.fixture
def guard_http_server() -> Iterator[tuple[str, int]]:
    original_service = DatasetApiHandler.service
    DatasetApiHandler.service = cast(DatasetDiscoveryService, _ServiceForErrorPaths())

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    host, port = sock.getsockname()
    sock.close()

    from http.server import ThreadingHTTPServer

    server = ThreadingHTTPServer((host, port), DatasetApiHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield host, port
    finally:
        server.shutdown()
        server.server_close()
        DatasetApiHandler.service = original_service


def _read_json(url: str) -> dict[str, Any]:
    with urlopen(url, timeout=5) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def test_env_value_returns_default_for_missing_or_empty_values() -> None:
    assert _env_value({}, "A", "fallback") == "fallback"
    assert _env_value({"A": ""}, "A", "fallback") == "fallback"
    assert _env_value({"A": "value"}, "A", "fallback") == "value"


def test_schema_readiness_wraps_sqlalchemy_errors() -> None:
    class _BoomEngine:
        def connect(self) -> object:
            from sqlalchemy.exc import SQLAlchemyError

            raise SQLAlchemyError("boom")

    with pytest.raises(RuntimeError, match="schema is not ready"):
        _require_schema_readiness(
            engine=_BoomEngine(), expected_revision="0010_source_profile_metadata"
        )


def test_resolve_expected_revision_prefers_env_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DISCOVERY_EXPECTED_DB_REVISION", "override_head")

    assert _resolve_expected_revision(environment=os.environ) == "override_head"


def test_resolve_expected_revision_uses_alembic_head_when_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeScriptDirectory:
        def get_current_head(self) -> str:
            return "derived_head"

    monkeypatch.delenv("DISCOVERY_EXPECTED_DB_REVISION", raising=False)
    monkeypatch.setattr(
        "src.http_api_server.ScriptDirectory.from_config",
        lambda _config: _FakeScriptDirectory(),
    )

    assert _resolve_expected_revision(environment={}) == "derived_head"


def test_make_service_builds_persisted_runtime_service(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    class _FakeEngine:
        pass

    class _FakeRepository:
        def __init__(self, *, engine: object) -> None:
            captured["repo_engine"] = engine

    class _FakeService:
        def __init__(self, repository: object) -> None:
            captured["service_repo"] = repository

    def _fake_create_engine(
        database_url: str, *, pool_pre_ping: bool, poolclass: object
    ) -> _FakeEngine:
        captured["database_url"] = database_url
        captured["pool_pre_ping"] = pool_pre_ping
        captured["poolclass"] = poolclass
        return _FakeEngine()

    def _fake_require_schema_readiness(*, engine: object, expected_revision: str) -> None:
        captured["schema_engine"] = engine
        captured["expected_revision"] = expected_revision

    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@h:1234/n")
    monkeypatch.setenv("DISCOVERY_EXPECTED_DB_REVISION", "0010_source_profile_metadata")
    monkeypatch.setattr("src.http_api_server.create_engine", _fake_create_engine)
    monkeypatch.setattr(
        "src.http_api_server._require_schema_readiness", _fake_require_schema_readiness
    )
    monkeypatch.setattr("src.http_api_server.PersistedDatasetDiscoveryRepository", _FakeRepository)
    monkeypatch.setattr("src.http_api_server.DatasetDiscoveryService", _FakeService)

    service = _make_service()

    assert captured["database_url"] == "postgresql+psycopg://u:p@h:1234/n"
    assert captured["expected_revision"] == "0010_source_profile_metadata"
    assert captured["repo_engine"] is captured["schema_engine"]
    assert service is not None


def test_http_handler_health_not_found_and_error_branches(
    guard_http_server: tuple[str, int],
) -> None:
    host, port = guard_http_server

    health = _read_json(f"http://{host}:{port}/api/health")
    with pytest.raises(HTTPError) as not_found_exc:
        urlopen(f"http://{host}:{port}/api/nope", timeout=5)  # noqa: S310
    not_found = json.loads(not_found_exc.value.read().decode("utf-8"))

    assert health == {"status": "ok"}
    assert not_found["error"]["code"] == "not_found"

    with pytest.raises(HTTPError) as search_exc:
        urlopen(f"http://{host}:{port}/api/datasets/search?q=x", timeout=5)  # noqa: S310
    assert search_exc.value.code == 400

    with pytest.raises(HTTPError) as recent_exc:
        urlopen(f"http://{host}:{port}/api/datasets/recent", timeout=5)  # noqa: S310
    assert recent_exc.value.code == 400

    with pytest.raises(HTTPError) as catalog_exc:
        urlopen(f"http://{host}:{port}/api/datasets?source_id=bad", timeout=5)  # noqa: S310
    assert catalog_exc.value.code == 400

    with pytest.raises(HTTPError) as detail_exc:
        urlopen(f"http://{host}:{port}/api/datasets/UNKNOWN", timeout=5)  # noqa: S310
    assert detail_exc.value.code == 404

    with pytest.raises(HTTPError) as csv_exc:
        urlopen(f"http://{host}:{port}/api/datasets/UNKNOWN.csv", timeout=5)  # noqa: S310
    assert csv_exc.value.code == 404


def test_http_handler_returns_500_when_service_not_initialized() -> None:
    original_service = DatasetApiHandler.service
    DatasetApiHandler.service = None

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    host, port = sock.getsockname()
    sock.close()

    from http.server import ThreadingHTTPServer

    server = ThreadingHTTPServer((host, port), DatasetApiHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with pytest.raises(HTTPError) as exc_info:
            urlopen(f"http://{host}:{port}/api/datasets/search", timeout=5)  # noqa: S310
        assert exc_info.value.code == 500
    finally:
        server.shutdown()
        server.server_close()
        DatasetApiHandler.service = original_service


def test_main_wires_server_and_calls_serve_forever(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    class _FakeServer:
        def __init__(self, address: tuple[str, int], handler: type[DatasetApiHandler]) -> None:
            captured["address"] = address
            captured["handler"] = handler

        def serve_forever(self) -> None:
            captured["served"] = True

    monkeypatch.setattr("src.http_api_server._make_service", lambda: object())
    monkeypatch.setattr("src.http_api_server._make_auth_service", lambda: object())
    monkeypatch.setattr("src.http_api_server._make_notification_service", lambda: object())
    monkeypatch.setattr("src.http_api_server.ThreadingHTTPServer", _FakeServer)
    monkeypatch.setattr(
        "src.http_api_server.argparse.ArgumentParser.parse_args",
        lambda self: Namespace(host="127.0.0.1", port=18080),
    )

    main()

    assert captured["address"] == ("127.0.0.1", 18080)
    assert captured["handler"] is DatasetApiHandler
    assert captured["served"] is True
