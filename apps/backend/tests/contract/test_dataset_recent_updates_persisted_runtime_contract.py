"""US1 persisted-runtime contract coverage for recent updates."""

# ruff: noqa: D103, E501, PLR2004, RET501, PLR1711

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService


class _PersistedRecentRepoStub:
    def search_datasets(self, *, query_text: str | None, page: int, page_size: int):
        del query_text, page, page_size
        return [], 0

    def list_recent_datasets(self, *, limit: int):
        assert limit == 5
        return [
            {
                "dataset_id": "ENERGY.US.GASREGW",
                "source": {"id": "fred", "name": "FRED"},
                "title": "US Regular Gas Price",
                "description": "Consumer gasoline prices",
                "geographic_scope": "US",
                "topic_tags": ["energy"],
                "latest_update_at": "2026-03-20T00:00:00+00:00",
                "has_recent_notification": True,
                "canonical_trend_descriptor": {
                    "descriptor_state": "available",
                    "trend_label": "strong_sustained_uptrend",
                    "direction": "up",
                    "strength": "strong",
                    "selected_lookback_points": 100,
                    "observed_on": "2026-03-20",
                    "reason_code": None,
                },
                "metadata": {},
            }
        ]

    def list_catalog_datasets(
        self,
        *,
        query_text: str | None,
        options: dict[str, object],
    ):
        del query_text, options
        return [], 0

    def list_catalog_aggregations(
        self, *, query_text: str | None, options: dict[str, object] | None = None
    ):
        del query_text, options
        return {"total_dataset_count": 0, "sources": [], "categories": []}

    def get_dataset_detail(self, *, dataset_id: str):
        del dataset_id
        return None

    def list_dataset_observations(self, *, dataset_id: str, from_date, to_date):
        del dataset_id, from_date, to_date
        return []


def test_recent_updates_contract_uses_persisted_recency_payload() -> None:
    service = DatasetDiscoveryService(_PersistedRecentRepoStub())

    payload = service.list_recent_updates(limit=5)

    assert payload["limit"] == 5
    assert payload["items"][0]["dataset_id"] == "ENERGY.US.GASREGW"
    assert payload["items"][0]["has_recent_notification"] is True
    assert payload["items"][0]["canonical_trend_descriptor"]["descriptor_state"] == "available"
    assert payload["sort"] == "event_timestamp_desc,title_asc,dataset_id_asc"
