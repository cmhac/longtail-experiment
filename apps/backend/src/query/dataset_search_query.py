"""Dataset search query execution entrypoint."""

from __future__ import annotations

from src.contract.query.dataset_search_query import DatasetSearchResponse

from .dataset_discovery_service import DatasetDiscoveryService


def execute_dataset_search(
    service: DatasetDiscoveryService,
    *,
    query_text: str | None,
    page: int | None,
    page_size: int | None,
) -> DatasetSearchResponse:
    """Execute search query and return validated contract response."""
    payload = service.search_datasets(
        query_text=query_text,
        page=page,
        page_size=page_size,
    )
    return DatasetSearchResponse.model_validate(payload)
