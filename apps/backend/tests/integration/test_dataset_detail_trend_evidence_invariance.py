"""Integration tests for canonical and lookback evidence invariance."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository


def test_detail_trend_evidence_semantics_remain_intact() -> None:
    datasets, observations = build_discovery_rows()
    service = DatasetDiscoveryService(
        InMemoryDatasetDiscoveryRepository(datasets=datasets, observations=observations)
    )

    payload = service.get_dataset_detail(dataset_id="UNRATE", from_date=None, to_date=None)

    canonical = payload["canonical_trend_descriptor"]
    assert canonical["descriptor_version"] == "v2"
    assert canonical["descriptor_state"] in {"available", "unavailable"}
    assert isinstance(payload["lookback_trend_evidence"], list)
