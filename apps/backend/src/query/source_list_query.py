"""Source list query execution entrypoint."""

from __future__ import annotations

from src.contract.query.source_discovery_query import SourceListResponse

from .dataset_discovery_service import DatasetDiscoveryService


def execute_source_list(service: DatasetDiscoveryService) -> SourceListResponse:
    """Execute source list query and return validated contract response."""
    payload = service.list_sources()
    return SourceListResponse.model_validate(payload)
