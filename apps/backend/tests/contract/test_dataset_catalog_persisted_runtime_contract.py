"""US1 persisted-runtime contract coverage for catalog reads."""

# ruff: noqa: D103, E501, RET501, PLR1711

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService

DEFAULT_PAGE_SIZE = 20


class _PersistedCatalogRepoStub:
    def search_datasets(self, *, query_text: str | None, page: int, page_size: int):
        del query_text, page, page_size
        return [], 0

    def list_recent_datasets(self, *, limit: int):
        del limit
        return []

    def list_catalog_datasets(
        self,
        *,
        query_text: str | None,
        options: dict[str, object],
    ):
        del query_text, options
        return [
            {
                "dataset_id": "INT.US.FEDFUNDS",
                "source": {"id": "fred", "name": "FRED"},
                "title": "Effective Federal Funds Rate",
                "description": "Policy rate",
                "geographic_scope": "US",
                "topic_tags": ["interest rates"],
                "latest_update_at": "2026-03-06T00:00:00+00:00",
                "metadata": {},
            }
        ], 1

    def list_catalog_aggregations(self, *, query_text: str | None):
        del query_text
        return {
            "total_dataset_count": 1,
            "sources": [{"source": {"id": "fred", "name": "FRED"}, "dataset_count": 1}],
            "categories": [{"value": "interest rates", "dataset_count": 1}],
        }

    def get_dataset_detail(self, *, dataset_id: str):
        del dataset_id
        return None

    def list_dataset_observations(self, *, dataset_id: str, from_date, to_date):
        del dataset_id, from_date, to_date
        return []

    def group_catalog_by_source(self, rows):
        del rows
        return [
            {
                "source": {"id": "fred", "name": "FRED"},
                "dataset_count": 1,
                "dataset_ids": ["INT.US.FEDFUNDS"],
            }
        ]


def test_catalog_contract_uses_persisted_metadata_and_grouping() -> None:
    service = DatasetDiscoveryService(_PersistedCatalogRepoStub())

    payload = service.list_catalog(
        query_text="federal",
        options={
            "source_id": "fred",
            "category": None,
            "sort": None,
            "page": 1,
            "page_size": DEFAULT_PAGE_SIZE,
        },
        group_by_source=True,
    )

    assert payload["total_items"] == 1
    assert payload["aggregations"]["categories"][0]["value"] == "interest rates"
    assert payload["items"][0]["dataset_id"] == "INT.US.FEDFUNDS"
    assert payload["groups"][0]["source"]["id"] == "fred"
    assert payload["page"] == 1
    assert payload["page_size"] == DEFAULT_PAGE_SIZE
    assert payload["total_pages"] == 1
    assert payload["sort"] == "latest_update_at_desc,title_asc,dataset_id_asc"
