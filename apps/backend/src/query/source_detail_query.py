"""Source detail query execution entrypoint."""

from __future__ import annotations

from src.contract.query.source_discovery_query import SourceDetailResponse

from .dataset_discovery_service import DatasetDiscoveryService


def execute_source_detail(
    service: DatasetDiscoveryService,
    *,
    source_id: str,
) -> SourceDetailResponse:
    """Execute source detail query and return validated contract response."""
    payload = service.get_source_detail(source_id=source_id)
    return SourceDetailResponse.model_validate(payload)
