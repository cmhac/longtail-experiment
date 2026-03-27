"""Geography detail query execution entrypoint."""

from __future__ import annotations

from src.contract.query.metadata_discovery_query import GeographyDetailResponse

from .dataset_discovery_service import DatasetDiscoveryService


def execute_geography_detail(
    service: DatasetDiscoveryService,
    *,
    geography_id: str,
    page: int | None,
    page_size: int | None,
) -> GeographyDetailResponse:
    """Execute geography detail query and return validated contract response."""
    payload = service.get_geography_detail(
        geography_id=geography_id,
        page=page,
        page_size=page_size,
    )
    return GeographyDetailResponse.model_validate(payload)
