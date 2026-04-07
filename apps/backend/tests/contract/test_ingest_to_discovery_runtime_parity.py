"""US2 integration checks for ingest-to-discovery runtime parity behavior."""

# ruff: noqa: D103, E501

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_service import DatasetDiscoveryService


class _ParityRepoStub:
    def __init__(self) -> None:
        self._stage = "baseline"

    def apply_ingest_update(self) -> None:
        self._stage = "post_ingest"

    def _current_item(self) -> dict[str, object]:
        latest = (
            "2026-03-06T00:00:00+00:00"
            if self._stage == "baseline"
            else "2026-03-20T00:00:00+00:00"
        )
        return {
            "dataset_id": "INT.US.FEDFUNDS",
            "source": {"id": "fred", "name": "FRED"},
            "title": "Effective Federal Funds Rate",
            "description": "Policy rate",
            "geographic_scope": "US",
            "topic_tags": ["interest rates"],
            "latest_update_at": latest,
            "metadata": {},
        }

    def search_datasets(self, *, query_text: str | None, page: int, page_size: int):
        del query_text, page, page_size
        item = self._current_item()
        return [item], 1

    def list_recent_datasets(self, *, limit: int):
        del limit
        return [self._current_item()]

    def list_catalog_datasets(
        self,
        *,
        query_text: str | None,
        options: dict[str, object],
    ):
        del query_text, options
        return [self._current_item()], 1

    def list_catalog_aggregations(
        self, *, query_text: str | None, options: dict[str, object] | None = None
    ):
        del query_text, options
        return {"total_dataset_count": 1, "sources": [], "categories": []}

    def get_dataset_detail(self, *, dataset_id: str):
        if dataset_id != "INT.US.FEDFUNDS":
            return None
        return self._current_item()

    def list_dataset_observations(self, *, dataset_id: str, from_date, to_date):
        del from_date, to_date
        if dataset_id != "INT.US.FEDFUNDS":
            return []
        if self._stage == "baseline":
            return [
                {
                    "observed_on": "2026-01-01",
                    "value": 4.33,
                    "reported_at": "2026-03-06T00:00:00+00:00",
                    "attributes": {},
                }
            ]
        return [
            {
                "observed_on": "2026-01-01",
                "value": 4.33,
                "reported_at": "2026-03-06T00:00:00+00:00",
                "attributes": {},
            },
            {
                "observed_on": "2026-02-01",
                "value": 4.41,
                "reported_at": "2026-03-20T00:00:00+00:00",
                "attributes": {},
            },
        ]


def test_ingest_to_discovery_runtime_parity_detects_endpoint_delta() -> None:
    repo = _ParityRepoStub()
    service = DatasetDiscoveryService(repo)

    baseline_recent = service.list_recent_updates(limit=5)
    baseline_detail = service.get_dataset_detail(
        dataset_id="INT.US.FEDFUNDS",
        from_date=None,
        to_date=None,
    )

    repo.apply_ingest_update()

    post_recent = service.list_recent_updates(limit=5)
    post_detail = service.get_dataset_detail(
        dataset_id="INT.US.FEDFUNDS",
        from_date=None,
        to_date=None,
    )

    assert (
        baseline_recent["items"][0]["latest_update_at"]
        != post_recent["items"][0]["latest_update_at"]
    )
    assert len(post_detail["observations"]) > len(baseline_detail["observations"])
