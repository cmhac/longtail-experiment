"""US2 HTTP regression coverage for dataset detail as-of descriptor serialization."""

# ruff: noqa: D103, E501, PLR2004

from __future__ import annotations

import json
import socket
import sys
import threading
from collections.abc import Iterator
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.http_api_server import DatasetApiHandler
from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.contract.fixtures.dataset_detail_asof_trend_fixtures import (
    build_observation_asof_available_descriptor,
)
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


@pytest.fixture
def http_server() -> Iterator[tuple[str, int]]:
    datasets, observations = build_discovery_rows()
    seeded_observations = [dict(observation) for observation in observations]
    seeded_observations[0]["as_of_trend_descriptor"] = build_observation_asof_available_descriptor(
        observed_on="2026-01-01",
        selected_lookback_points=10,
    )
    service = DatasetDiscoveryService(
        InMemoryDatasetDiscoveryRepository(
            datasets=datasets,
            observations=seeded_observations,
            canonical_trends_by_dataset={
                "UNRATE": {
                    "descriptor_state": "available",
                    "trend_label": "mild_sustained_downtrend",
                    "direction": "down",
                    "strength": "mild",
                    "selected_lookback_points": 25,
                    "observed_on": "2026-02-01",
                    "reason_code": None,
                }
            },
            lookback_snapshots_by_dataset={
                "UNRATE": [
                    {
                        "lookback_points": 25,
                        "applicability_state": "applicable",
                        "outcome_state": "significant_trend",
                        "trend_label": "mild_sustained_downtrend",
                        "direction": "down",
                        "strength": "mild",
                        "reason_code": None,
                    }
                ]
            },
        )
    )
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
    with urlopen(url, timeout=5) as response:  # noqa: S310 - localhost test fixture
        return json.loads(response.read().decode("utf-8"))


def test_http_dataset_detail_serializes_observation_asof_descriptor_contract(
    http_server: tuple[str, int],
) -> None:
    host, port = http_server
    detail_payload = _read_json(f"http://{host}:{port}/api/datasets/UNRATE")

    assert detail_payload["dataset_id"] == "UNRATE"
    assert "canonical_trend_descriptor" in detail_payload
    assert "lookback_trend_snapshots" in detail_payload
    assert all("as_of_trend_descriptor" in item for item in detail_payload["observations"])
    assert detail_payload["observations"][0]["as_of_trend_descriptor"] == {
        "descriptor_state": "available",
        "descriptor_version": "v2",
        "trend_label": "mild_sustained_downtrend",
        "direction": "down",
        "strength": "mild",
        "dominant_measure_family": "none",
        "confidence_score": None,
        "selected_lookback_points": 10,
        "observed_on": "2026-01-01",
        "reason_code": None,
    }
