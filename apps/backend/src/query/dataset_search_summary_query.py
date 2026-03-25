"""Homepage search summary query execution entrypoint."""

from __future__ import annotations

from src.contract.query.dataset_search_query import SearchScopeSummaryResponse

from .dataset_discovery_service import DatasetDiscoveryService


def execute_search_summary(service: DatasetDiscoveryService) -> SearchScopeSummaryResponse:
    """Execute homepage search summary query and return validated response."""
    payload = service.get_search_summary()
    return SearchScopeSummaryResponse.model_validate(payload)
