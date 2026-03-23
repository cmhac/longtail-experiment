"""US1 integration tests for HTTP runtime persisted discovery endpoints."""

# ruff: noqa: D103, E501, PLR2004

from __future__ import annotations

import json
import socket
import sys
import threading
from collections.abc import Iterator
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.errors import ContractQueryError
from src.http_api_server import DatasetApiHandler
from src.query.dataset_discovery_service import DatasetDiscoveryService


class _PersistedHttpRepoStub:
    def __init__(self) -> None:
        self._dataset = {
            "dataset_id": "INT.US.FEDFUNDS",
            "source": {"id": "fred", "name": "FRED"},
            "title": "Effective Federal Funds Rate",
            "description": "Policy rate",
            "geographic_scope": "US",
            "topic_tags": ["interest rates"],
            "latest_update_at": "2026-03-06T00:00:00+00:00",
            "metadata": {"frequency_granularity": "daily"},
        }

    def search_datasets(self, *, query_text: str | None, page: int, page_size: int):
        del query_text, page, page_size
        return [self._dataset], 1

    def list_recent_datasets(self, *, limit: int):
        del limit
        return [self._dataset]

    def list_catalog_datasets(
        self, *, query_text: str | None, source_id: str | None, page: int, page_size: int
    ):
        del query_text, source_id, page, page_size
        return [self._dataset], 1

    def get_dataset_detail(self, *, dataset_id: str):
        if dataset_id != "INT.US.FEDFUNDS":
            return None
        return dict(self._dataset)

    def list_dataset_observations(self, *, dataset_id: str, from_date, to_date):
        del from_date, to_date
        if dataset_id != "INT.US.FEDFUNDS":
            raise ContractQueryError("dataset_not_found")
        return [
            {
                "observed_on": "2026-01-01",
                "value": 4.33,
                "reported_at": "2026-03-06T00:00:00+00:00",
                "attributes": {},
            }
        ]


@pytest.fixture
def http_server() -> Iterator[tuple[str, int]]:
    service = DatasetDiscoveryService(_PersistedHttpRepoStub())
    original_service = DatasetApiHandler.service
    DatasetApiHandler.service = service

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


def _read_json(url: str) -> dict[str, Any]:
    with urlopen(url, timeout=5) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def test_http_runtime_persisted_endpoints_return_expected_payloads(
    http_server: tuple[str, int],
) -> None:
    host, port = http_server

    search_payload: dict[str, Any] = _read_json(f"http://{host}:{port}/api/datasets/search")
    recent_payload: dict[str, Any] = _read_json(f"http://{host}:{port}/api/datasets/recent")
    catalog_payload: dict[str, Any] = _read_json(f"http://{host}:{port}/api/datasets")
    detail_payload: dict[str, Any] = _read_json(
        f"http://{host}:{port}/api/datasets/INT.US.FEDFUNDS"
    )

    assert search_payload["items"][0]["dataset_id"] == "INT.US.FEDFUNDS"
    assert recent_payload["items"][0]["dataset_id"] == "INT.US.FEDFUNDS"
    assert catalog_payload["items"][0]["dataset_id"] == "INT.US.FEDFUNDS"
    assert detail_payload["dataset_id"] == "INT.US.FEDFUNDS"


def test_http_runtime_unknown_dataset_returns_not_found(http_server: tuple[str, int]) -> None:
    host, port = http_server

    with pytest.raises(HTTPError) as exc_info:
        urlopen(f"http://{host}:{port}/api/datasets/UNKNOWN", timeout=5)  # noqa: S310

    assert exc_info.value.code == HTTPStatus.NOT_FOUND
    payload = json.loads(exc_info.value.read().decode("utf-8"))
    assert payload["error"]["code"] == "dataset_not_found"
