"""US1 persisted-runtime contract coverage for dataset detail reads."""

# ruff: noqa: D103, E501

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService


class _PersistedDetailRepoStub:
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
        return [], 0

    def list_catalog_aggregations(self, *, query_text: str | None):
        del query_text
        return {"total_dataset_count": 0, "sources": [], "categories": []}

    def get_dataset_detail(self, *, dataset_id: str):
        if dataset_id != "INT.US.FEDFUNDS":
            return None
        return {
            "dataset_id": "INT.US.FEDFUNDS",
            "source": {"id": "fred", "name": "FRED"},
            "title": "Effective Federal Funds Rate",
            "description": "Policy rate",
            "geographic_scope": "US",
            "topic_tags": ["interest rates"],
            "metadata": {},
        }

    def list_dataset_observations(self, *, dataset_id: str, from_date, to_date):
        del from_date, to_date
        assert dataset_id == "INT.US.FEDFUNDS"
        return [
            {
                "observed_on": "2026-01-01",
                "value": 4.33,
                "reported_at": "2026-03-06T00:00:00+00:00",
                "attributes": {"unit_type": "percent"},
            },
            {
                "observed_on": "2026-02-01",
                "value": 4.41,
                "reported_at": "2026-03-06T00:00:00+00:00",
                "attributes": {},
            },
        ]


def test_detail_contract_uses_persisted_observations_and_sort_metadata() -> None:
    service = DatasetDiscoveryService(_PersistedDetailRepoStub())

    payload = service.get_dataset_detail(
        dataset_id="INT.US.FEDFUNDS",
        from_date=None,
        to_date=None,
    )

    assert payload["dataset_id"] == "INT.US.FEDFUNDS"
    assert [point["observed_on"] for point in payload["observations"]] == [
        "2026-01-01",
        "2026-02-01",
    ]
    assert payload["metadata"]["unit_type"] == "percent"
    assert payload["observation_sort"] == "observed_on_asc,reported_at_asc"
