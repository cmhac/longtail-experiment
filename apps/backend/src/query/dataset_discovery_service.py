"""Service orchestration for dataset discovery query workflows."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.contract.errors import ContractQueryError

from .dataset_discovery_validators import (
    normalize_page,
    normalize_page_size,
    normalize_query_text,
    normalize_recent_limit,
    parse_optional_date,
    validate_date_range,
)


class DatasetDiscoveryService:
    """Coordinates search, recent, catalog, and detail query behavior."""

    def __init__(self, repository: Any) -> None:
        """Initialize service with a repository providing discovery read methods."""
        missing_methods = [
            method_name
            for method_name in (
                "search_datasets",
                "list_recent_datasets",
                "list_catalog_datasets",
                "get_dataset_detail",
                "list_dataset_observations",
            )
            if not hasattr(repository, method_name)
        ]
        if missing_methods:
            missing = ", ".join(missing_methods)
            raise ContractQueryError(
                f"Repository does not provide required discovery methods: {missing}"
            )
        self._repository = repository

    def search_datasets(
        self,
        *,
        query_text: str | None,
        page: int | None,
        page_size: int | None,
    ) -> dict[str, Any]:
        """Return paginated discovery search response."""
        if not hasattr(self._repository, "search_datasets"):
            raise ContractQueryError("Repository does not provide search_datasets")

        normalized_query = normalize_query_text(query_text)
        normalized_page = normalize_page(page)
        normalized_page_size = normalize_page_size(page_size)

        items, total_items = self._repository.search_datasets(
            query_text=normalized_query,
            page=normalized_page,
            page_size=normalized_page_size,
        )
        if not isinstance(items, list) or not isinstance(total_items, int):
            raise ContractQueryError("Repository returned invalid search payload")
        total_pages = ((total_items - 1) // normalized_page_size + 1) if total_items else 0

        return {
            "items": deepcopy(items),
            "page": normalized_page,
            "page_size": normalized_page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "sort": "latest_update_at_desc,title_asc,dataset_id_asc",
        }

    def list_recent_updates(self, *, limit: int | None) -> dict[str, Any]:
        """Return recent dataset updates payload."""
        if not hasattr(self._repository, "list_recent_datasets"):
            raise ContractQueryError("Repository does not provide list_recent_datasets")

        normalized_limit = normalize_recent_limit(limit)
        items = self._repository.list_recent_datasets(limit=normalized_limit)
        if not isinstance(items, list):
            raise ContractQueryError("Repository returned invalid recent updates payload")
        return {
            "items": deepcopy(items),
            "limit": normalized_limit,
            "sort": "latest_update_at_desc,title_asc,dataset_id_asc",
        }

    def list_catalog(
        self,
        *,
        query_text: str | None,
        source_id: str | None,
        page: int | None,
        page_size: int | None,
        group_by_source: bool,
    ) -> dict[str, Any]:
        """Return catalog results with optional source grouping."""
        if not hasattr(self._repository, "list_catalog_datasets"):
            raise ContractQueryError("Repository does not provide list_catalog_datasets")

        normalized_query = normalize_query_text(query_text)
        normalized_page = normalize_page(page)
        normalized_page_size = normalize_page_size(page_size)
        normalized_source = source_id.strip() if source_id is not None else None

        items, total_items = self._repository.list_catalog_datasets(
            query_text=normalized_query,
            source_id=normalized_source,
            page=normalized_page,
            page_size=normalized_page_size,
        )
        if not isinstance(items, list) or not isinstance(total_items, int):
            raise ContractQueryError("Repository returned invalid catalog payload")
        total_pages = ((total_items - 1) // normalized_page_size + 1) if total_items else 0

        groups: list[dict[str, Any]] = []
        if group_by_source and hasattr(self._repository, "group_catalog_by_source"):
            groups = self._repository.group_catalog_by_source(items)
            if not isinstance(groups, list):
                raise ContractQueryError("Repository returned invalid source grouping payload")

        return {
            "items": deepcopy(items),
            "groups": deepcopy(groups),
            "page": normalized_page,
            "page_size": normalized_page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "sort": "source_name_asc,title_asc,dataset_id_asc",
        }

    def get_dataset_detail(
        self,
        *,
        dataset_id: str,
        from_date: str | None,
        to_date: str | None,
    ) -> dict[str, Any]:
        """Return one dataset detail payload with chronological observations."""
        if not hasattr(self._repository, "get_dataset_detail"):
            raise ContractQueryError("Repository does not provide get_dataset_detail")
        if not hasattr(self._repository, "list_dataset_observations"):
            raise ContractQueryError("Repository does not provide list_dataset_observations")

        normalized_dataset_id = dataset_id.strip()
        if not normalized_dataset_id:
            raise ContractQueryError("dataset_id must be provided")

        from_value = parse_optional_date(from_date, field_name="from_date")
        to_value = parse_optional_date(to_date, field_name="to_date")
        validate_date_range(from_value, to_value)

        metadata = self._repository.get_dataset_detail(dataset_id=normalized_dataset_id)
        if metadata is None:
            raise ContractQueryError("dataset_not_found")
        if not isinstance(metadata, dict):
            raise ContractQueryError("Repository returned invalid dataset detail payload")

        observations = self._repository.list_dataset_observations(
            dataset_id=normalized_dataset_id,
            from_date=from_value,
            to_date=to_value,
        )
        if not isinstance(observations, list):
            raise ContractQueryError("Repository returned invalid observations payload")
        return {
            **deepcopy(metadata),
            "observations": deepcopy(observations),
            "observation_sort": "observed_on_asc,reported_at_asc",
        }
