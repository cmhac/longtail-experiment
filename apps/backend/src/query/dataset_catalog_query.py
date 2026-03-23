"""Dataset catalog query execution entrypoint."""

from __future__ import annotations

from typing import Any, cast

from src.contract.query.dataset_catalog_query import DatasetCatalogResponse

from .dataset_catalog_grouping import project_catalog_source_groups
from .dataset_discovery_service import DatasetDiscoveryService


def execute_dataset_catalog(  # noqa: PLR0913
    service: DatasetDiscoveryService,
    *,
    query_text: str | None,
    source_id: str | None,
    page: int | None,
    page_size: int | None,
    group_by_source: bool,
) -> DatasetCatalogResponse:
    """Execute catalog query and return validated contract response."""
    payload = service.list_catalog(
        query_text=query_text,
        source_id=source_id,
        page=page,
        page_size=page_size,
        group_by_source=group_by_source,
    )
    if group_by_source:
        payload["groups"] = project_catalog_source_groups(
            cast(list[dict[str, Any]], payload["items"])
        )
    return DatasetCatalogResponse.model_validate(payload)
