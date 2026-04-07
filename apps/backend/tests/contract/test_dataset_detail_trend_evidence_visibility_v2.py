"""US2 contract test for detail endpoint evidence visibility semantics."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository
from tests.fixtures.trend_v2_payloads import canonical_available_v2, lookback_evidence_v2


def test_dataset_detail_includes_lookback_evidence_fields_for_v2() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
        canonical_trends_by_dataset={"UNRATE": canonical_available_v2()},
        lookback_snapshots_by_dataset={"UNRATE": lookback_evidence_v2()},
    )
    service = DatasetDiscoveryService(repository)

    response = service.get_dataset_detail(dataset_id="UNRATE", from_date=None, to_date=None)
    assert response["canonical_trend_descriptor"]["descriptor_version"] == "v2"
    assert len(response["lookback_trend_snapshots"]) >= 1
    assert "theil_sen_slope" in response["lookback_trend_snapshots"][0]
