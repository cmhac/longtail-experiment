"""Dataset as-of trend query execution entrypoint."""

from __future__ import annotations

from src.contract.query.trend_descriptor_v2 import ObservationAsOfTrendV2Response

from .dataset_discovery_service import DatasetDiscoveryService


def execute_dataset_asof_trend(
    service: DatasetDiscoveryService,
    *,
    dataset_id: str,
    as_of_observed_on: str,
) -> ObservationAsOfTrendV2Response:
    """Execute as-of trend query and return validated v2 contract response."""
    payload = service.get_dataset_as_of_trend(
        dataset_id=dataset_id,
        as_of_observed_on=as_of_observed_on,
    )
    return ObservationAsOfTrendV2Response.model_validate(payload)
