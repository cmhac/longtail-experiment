"""Integration tests for HTTP runtime source discovery endpoints."""

from __future__ import annotations

import json
import socket
import sys
import threading
from collections.abc import Iterator
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import cast
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.http_api_server import DatasetApiHandler
from src.query.dataset_discovery_service import DatasetDiscoveryService

EXPECTED_DATASET_COUNT = 2


class _SourceHttpRepoStub:
    def __init__(self) -> None:
        self._datasets = [
            {
                "dataset_id": "UNRATE",
                "source": {"id": "fred", "name": "FRED"},
                "title": "Unemployment Rate",
                "description": "Labor market measure",
                "geographic_scope": "US",
                "topic_tags": ["labor"],
                "latest_update_at": "2026-03-10T00:00:00+00:00",
                "metadata": {"source_type": "external"},
            },
            {
                "dataset_id": "CPIAUCSL",
                "source": {"id": "fred", "name": "FRED"},
                "title": "Consumer Price Index",
                "description": "Price level measure",
                "geographic_scope": "US",
                "topic_tags": ["inflation"],
                "latest_update_at": "2026-03-09T00:00:00+00:00",
                "metadata": {"source_type": "external"},
            },
        ]

    def search_datasets(self, *, query_text: str | None, page: int, page_size: int):
        del query_text, page, page_size
        return list(self._datasets), len(self._datasets)

    def list_recent_datasets(self, *, limit: int):
        return list(self._datasets[:limit])

    def get_search_summary(self):
        return {
            "active_dataset_count": 2,
            "active_source_count": 1,
            "generated_at": "2026-03-24T00:00:00+00:00",
        }

    def search_suggestions(self, *, query_text: str, limit: int):
        del query_text, limit
        return []

    def list_catalog_datasets(
        self,
        *,
        query_text: str | None,
        options: dict[str, object],
    ):
        del query_text, options
        return list(self._datasets), len(self._datasets)

    def list_catalog_aggregations(self, *, query_text: str | None):
        del query_text
        return {"total_dataset_count": 2, "sources": [], "categories": []}

    def get_dataset_detail(self, *, dataset_id: str):
        for item in self._datasets:
            if item["dataset_id"] == dataset_id:
                return dict(item)
        return None

    def list_dataset_observations(self, *, dataset_id: str, from_date, to_date):
        del dataset_id, from_date, to_date
        return []

    def list_sources(self):
        return [
            {
                "id": "fred",
                "name": "FRED",
                "dataset_count": 2,
                "source_type": "external",
            }
        ]

    def get_source_detail(self, *, source_id: str, page: int, page_size: int):
        if source_id != "fred":
            return None
        start = (page - 1) * page_size
        end = start + page_size
        items = list(self._datasets)[start:end]
        return {
            "source": {
                "id": "fred",
                "name": "FRED",
                "dataset_count": 2,
                "source_type": "external",
            },
            "items": items,
            "total_items": len(self._datasets),
        }


@pytest.fixture
def http_server() -> Iterator[tuple[str, int]]:
    """Start a temporary HTTP server backed by the source repo stub."""
    service = DatasetDiscoveryService(_SourceHttpRepoStub())
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


def _read_json(url: str) -> dict[str, object]:
    with urlopen(url, timeout=5) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def test_http_runtime_source_endpoints_return_expected_payloads(
    http_server: tuple[str, int],
) -> None:
    """Serve source list and detail payloads from the runtime HTTP layer."""
    host, port = http_server

    source_list = _read_json(f"http://{host}:{port}/api/sources")
    source_detail = _read_json(f"http://{host}:{port}/api/sources/fred?page=1&page_size=1")
    source_list_items = source_list["items"]
    source_detail_payload = source_detail["source"]
    source_detail_items = source_detail["items"]

    assert source_list["total_items"] == 1
    assert isinstance(source_list_items, list)
    first_source_item = cast(dict[str, object], source_list_items[0])
    assert first_source_item["id"] == "fred"
    assert isinstance(source_detail_payload, dict)
    typed_source_detail_payload = cast(dict[str, object], source_detail_payload)
    assert typed_source_detail_payload["id"] == "fred"
    assert isinstance(source_detail_items, list)
    assert len(source_detail_items) == 1
    assert source_detail["page"] == 1
    assert source_detail["page_size"] == 1
    assert source_detail["total_items"] == EXPECTED_DATASET_COUNT
    assert source_detail["total_pages"] == EXPECTED_DATASET_COUNT


def test_http_runtime_unknown_source_returns_not_found(http_server: tuple[str, int]) -> None:
    """Return a source-not-found contract payload for unknown source ids."""
    host, port = http_server

    with pytest.raises(HTTPError) as exc_info:
        urlopen(f"http://{host}:{port}/api/sources/unknown", timeout=5)  # noqa: S310

    assert exc_info.value.code == HTTPStatus.NOT_FOUND
    payload = json.loads(exc_info.value.read().decode("utf-8"))
    assert payload["error"]["code"] == "source_not_found"
