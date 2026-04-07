"""US1 persisted-runtime contract coverage for dataset search."""

# ruff: noqa: D103, E501

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService


class _PersistedRepoStub:
    def __init__(self) -> None:
        self._items = [
            {
                "dataset_id": "INT.US.FEDFUNDS",
                "source": {"id": "fred", "name": "FRED"},
                "title": "Effective Federal Funds Rate",
                "description": "Policy rate",
                "geographic_scope": "US",
                "topic_tags": ["federal reserve", "interest rates"],
                "latest_update_at": "2026-03-06T00:00:00+00:00",
                "canonical_trend_descriptor": {
                    "descriptor_state": "available",
                    "trend_label": "mild_sustained_downtrend",
                    "direction": "down",
                    "strength": "mild",
                    "selected_lookback_points": 25,
                    "observed_on": "2026-03-06",
                    "reason_code": None,
                },
                "metadata": {},
            }
        ]

    def search_datasets(self, *, query_text: str | None, page: int, page_size: int):
        del query_text, page, page_size
        return self._items, len(self._items)

    def list_recent_datasets(self, *, limit: int):
        del limit
        return self._items

    def list_catalog_datasets(
        self,
        *,
        query_text: str | None,
        options: dict[str, object],
    ):
        del query_text, options
        return self._items, len(self._items)

    def list_catalog_aggregations(
        self, *, query_text: str | None, options: dict[str, object] | None = None
    ):
        del query_text, options
        return {"total_dataset_count": 1, "sources": [], "categories": []}

    def get_dataset_detail(self, *, dataset_id: str):
        del dataset_id
        return dict(self._items[0])

    def list_dataset_observations(self, *, dataset_id: str, from_date, to_date):
        del dataset_id, from_date, to_date
        return []


def test_search_contract_uses_persisted_dataset_shape() -> None:
    service = DatasetDiscoveryService(_PersistedRepoStub())

    payload = service.search_datasets(query_text="fed", page=1, page_size=20)

    assert payload["total_items"] == 1
    assert payload["items"][0]["dataset_id"] == "INT.US.FEDFUNDS"
    assert payload["items"][0]["source"]["name"] == "FRED"
    assert payload["items"][0]["canonical_trend_descriptor"]["descriptor_state"] == "available"
    assert payload["sort"] == "latest_update_at_desc,title_asc,dataset_id_asc"
