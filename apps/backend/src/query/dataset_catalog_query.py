"""Dataset catalog query execution entrypoint."""

from __future__ import annotations

from typing import Any, TypedDict, Unpack, cast

from src.contract.query.dataset_catalog_query import DatasetCatalogResponse

from .dataset_catalog_grouping import project_catalog_source_groups
from .dataset_discovery_service import DatasetDiscoveryService


class DatasetCatalogQueryParams(TypedDict):
    """Keyword params for dataset catalog query entrypoint."""

    query_text: str | None
    source_id: str | None
    category: str | None
    sort: str | None
    page: int | None
    page_size: int | None
    group_by_source: bool


def execute_dataset_catalog(
    service: DatasetDiscoveryService,
    **query: Unpack[DatasetCatalogQueryParams],
) -> DatasetCatalogResponse:
    """Execute catalog query and return validated contract response."""
    query_text = query.get("query_text")
    source_id = query.get("source_id")
    category = query.get("category")
    sort = query.get("sort")
    page = query.get("page")
    page_size = query.get("page_size")
    group_by_source = query.get("group_by_source", False)

    payload = service.list_catalog(
        query_text=query_text,
        options={
            "source_id": source_id,
            "category": category,
            "sort": sort,
            "page": page,
            "page_size": page_size,
        },
        group_by_source=group_by_source,
    )
    if group_by_source:
        payload["groups"] = project_catalog_source_groups(
            cast(list[dict[str, Any]], payload["items"])
        )
    return DatasetCatalogResponse.model_validate(payload)
