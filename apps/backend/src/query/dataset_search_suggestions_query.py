"""Likely dataset suggestions query execution entrypoint."""

from __future__ import annotations

from src.contract.query.dataset_search_query import DatasetSearchSuggestionsResponse

from .dataset_discovery_service import DatasetDiscoveryService


def execute_dataset_search_suggestions(
    service: DatasetDiscoveryService,
    *,
    query_text: str | None,
    limit: int | None,
) -> DatasetSearchSuggestionsResponse:
    """Execute likely-match suggestions query and return validated response."""
    payload = service.search_suggestions(query_text=query_text, limit=limit)
    return DatasetSearchSuggestionsResponse.model_validate(payload)
