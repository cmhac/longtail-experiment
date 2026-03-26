"""Geography detail query execution entrypoint."""

from __future__ import annotations

from src.contract.query.metadata_discovery_query import GeographyDetailResponse

from .dataset_discovery_service import DatasetDiscoveryService


def execute_geography_detail(
    service: DatasetDiscoveryService,
    *,
    geography_id: str,
) -> GeographyDetailResponse:
    """Execute geography detail query and return validated contract response."""
    payload = service.get_geography_detail(geography_id=geography_id)
    return GeographyDetailResponse.model_validate(payload)
