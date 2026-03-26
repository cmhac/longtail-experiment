"""Integration tests for HTTP runtime topic and geography discovery endpoints."""

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

EXPECTED_TOPIC_DATASET_COUNT = 1
EXPECTED_GEOGRAPHY_DATASET_COUNT = 2


class _MetadataHttpRepoStub:
    def __init__(self) -> None:
        self._datasets = [
            {
                "dataset_id": "UNRATE",
                "source": {"id": "fred", "name": "FRED"},
                "title": "Unemployment Rate",
                "description": "Labor market measure",
                "geographic_scope": "US",
                "topic_tags": ["labor", "employment"],
                "latest_update_at": "2026-03-10T00:00:00+00:00",
                "metadata": {"source_type": "external"},
            },
            {
                "dataset_id": "CPIAUCSL",
                "source": {"id": "fred", "name": "FRED"},
                "title": "Consumer Price Index",
                "description": "Price level measure",
                "geographic_scope": "US",
                "topic_tags": ["inflation", "prices"],
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

    def list_catalog_datasets(self, *, query_text: str | None, options: dict[str, object]):
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
        return []

    def get_source_detail(self, *, source_id: str):
        del source_id

    def get_topic_detail(self, *, topic_id: str):
        if topic_id != "inflation":
            return None
        return {
            "topic": {"id": "inflation", "label": "inflation", "dataset_count": 1},
            "datasets": [dict(self._datasets[1])],
        }

    def get_geography_detail(self, *, geography_id: str):
        if geography_id != "us":
            return None
        return {
            "geography": {"id": "us", "label": "US", "dataset_count": 2},
            "datasets": list(self._datasets),
        }


@pytest.fixture
def http_server() -> Iterator[tuple[str, int]]:
    """Serve the HTTP API against an in-memory metadata discovery stub."""
    service = DatasetDiscoveryService(_MetadataHttpRepoStub())
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


def test_http_runtime_metadata_endpoints_return_expected_payloads(
    http_server: tuple[str, int],
) -> None:
    """Return topic and geography detail payloads from runtime HTTP routes."""
    host, port = http_server

    topic_detail = _read_json(f"http://{host}:{port}/api/topics/inflation")
    geography_detail = _read_json(f"http://{host}:{port}/api/geographies/us")
    topic = topic_detail["topic"]
    topic_datasets = topic_detail["datasets"]
    geography = geography_detail["geography"]
    geography_datasets = geography_detail["datasets"]

    assert isinstance(topic, dict)
    assert isinstance(topic_datasets, list)
    assert isinstance(geography, dict)
    assert isinstance(geography_datasets, list)
    topic_record = cast(dict[str, object], topic)
    geography_record = cast(dict[str, object], geography)

    assert topic_record["id"] == "inflation"
    assert len(topic_datasets) == EXPECTED_TOPIC_DATASET_COUNT
    assert geography_record["id"] == "us"
    assert len(geography_datasets) == EXPECTED_GEOGRAPHY_DATASET_COUNT


def test_http_runtime_unknown_topic_returns_not_found(http_server: tuple[str, int]) -> None:
    """Return the topic not-found envelope when the topic id is unknown."""
    host, port = http_server

    with pytest.raises(HTTPError) as exc_info:
        urlopen(f"http://{host}:{port}/api/topics/unknown-topic", timeout=5)  # noqa: S310

    assert exc_info.value.code == HTTPStatus.NOT_FOUND
    payload = json.loads(exc_info.value.read().decode("utf-8"))
    assert payload["error"]["code"] == "topic_not_found"


def test_http_runtime_unknown_geography_returns_not_found(
    http_server: tuple[str, int],
) -> None:
    """Return the geography not-found envelope when the geography id is unknown."""
    host, port = http_server

    with pytest.raises(HTTPError) as exc_info:
        urlopen(f"http://{host}:{port}/api/geographies/unknown-geography", timeout=5)  # noqa: S310

    assert exc_info.value.code == HTTPStatus.NOT_FOUND
    payload = json.loads(exc_info.value.read().decode("utf-8"))
    assert payload["error"]["code"] == "geography_not_found"
