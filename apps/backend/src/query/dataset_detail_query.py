"""Dataset detail query execution entrypoint."""

from __future__ import annotations

from src.contract.query.dataset_detail_query import DatasetDetailResponse

from .dataset_discovery_service import DatasetDiscoveryService


def execute_dataset_detail(
    service: DatasetDiscoveryService,
    *,
    dataset_id: str,
    from_date: str | None,
    to_date: str | None,
) -> DatasetDetailResponse:
    """Execute detail query and return validated contract response."""
    payload = service.get_dataset_detail(
        dataset_id=dataset_id,
        from_date=from_date,
        to_date=to_date,
    )
    return DatasetDetailResponse.model_validate(payload)
