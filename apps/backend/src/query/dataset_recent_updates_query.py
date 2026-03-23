"""Recent updates query execution entrypoint."""

from __future__ import annotations

from src.contract.query.dataset_recent_updates_query import DatasetRecentUpdatesResponse

from .dataset_discovery_service import DatasetDiscoveryService


def execute_recent_updates(
    service: DatasetDiscoveryService,
    *,
    limit: int | None,
) -> DatasetRecentUpdatesResponse:
    """Execute recent-updates query and return validated response."""
    payload = service.list_recent_updates(limit=limit)
    return DatasetRecentUpdatesResponse.model_validate(payload)
