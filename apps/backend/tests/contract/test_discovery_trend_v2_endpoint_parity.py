"""US2 endpoint parity checks for v2 canonical and evidence payload surfaces."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository
from tests.fixtures.trend_v2_payloads import canonical_available_v2, lookback_evidence_v2


def test_discovery_endpoints_share_v2_canonical_shape() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
        canonical_trends_by_dataset={"UNRATE": canonical_available_v2()},
        lookback_snapshots_by_dataset={"UNRATE": lookback_evidence_v2()},
    )
    service = DatasetDiscoveryService(repository)

    search_payload = service.search_datasets(query_text=None, page=1, page_size=10)
    recent_payload = service.list_recent_updates(limit=5)
    detail_payload = service.get_dataset_detail(dataset_id="UNRATE", from_date=None, to_date=None)
    asof_payload = service.get_dataset_as_of_trend(
        dataset_id="UNRATE",
        as_of_observed_on="2026-03-01",
    )

    assert search_payload["items"][0]["canonical_trend_descriptor"]["descriptor_version"] == "v2"
    dataset_updates = [
        item for item in recent_payload["items"] if item["item_type"] == "dataset_update"
    ]
    assert dataset_updates[0]["canonical_trend_descriptor"]["descriptor_version"] == "v2"
    assert detail_payload["canonical_trend_descriptor"]["descriptor_version"] == "v2"
    assert asof_payload["canonical_trend_descriptor"]["descriptor_version"] == "v2"
    assert len(asof_payload["lookback_trend_evidence"]) >= 1
