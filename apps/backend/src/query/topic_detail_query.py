"""Topic detail query execution entrypoint."""

from __future__ import annotations

from src.contract.query.metadata_discovery_query import TopicDetailResponse

from .dataset_discovery_service import DatasetDiscoveryService


def execute_topic_detail(
    service: DatasetDiscoveryService,
    *,
    topic_id: str,
    page: int | None,
    page_size: int | None,
) -> TopicDetailResponse:
    """Execute topic detail query and return validated contract response."""
    payload = service.get_topic_detail(
        topic_id=topic_id,
        page=page,
        page_size=page_size,
    )
    return TopicDetailResponse.model_validate(payload)
