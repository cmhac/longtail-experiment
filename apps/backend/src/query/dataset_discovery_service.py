"""Service orchestration for dataset discovery query workflows."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from urllib.parse import quote

from src.contract.errors import ContractQueryError

from .dataset_discovery_validators import (
    normalize_page,
    normalize_page_size,
    normalize_query_text,
    normalize_recent_limit,
    parse_optional_date,
    validate_date_range,
)

DEFAULT_SUGGESTION_LIMIT = 5
MIN_SUGGESTION_LIMIT = 1
MAX_SUGGESTION_LIMIT = 10
SUPPORTED_UNIT_TYPES = {"usd", "percent", "number"}


def _normalize_unit_type(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    if normalized in SUPPORTED_UNIT_TYPES:
        return normalized
    return None


def _infer_unit_type_from_unit_label(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    if normalized == "":
        return None
    if "%" in normalized or "percent" in normalized:
        return "percent"
    if "$" in normalized or "dollar" in normalized:
        return "usd"
    return "number"


def _resolve_dataset_unit_type(
    metadata: dict[str, Any],
    observations: list[dict[str, Any]],
) -> str | None:
    metadata_unit_type = _normalize_unit_type(metadata.get("unit_type"))
    if metadata_unit_type is not None:
        return metadata_unit_type

    for observation in reversed(observations):
        if not isinstance(observation, dict):
            continue
        attributes = observation.get("attributes")
        if not isinstance(attributes, dict):
            continue
        resolved = _normalize_unit_type(attributes.get("unit_type"))
        if resolved is not None:
            return resolved

    for key in ("unit", "units"):
        resolved = _infer_unit_type_from_unit_label(metadata.get(key))
        if resolved is not None:
            return resolved

    return None


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

    def get_search_summary(self) -> dict[str, Any]:
        """Return aggregate summary counts for homepage search scope text."""
        if not hasattr(self._repository, "get_search_summary"):
            raise ContractQueryError("Repository does not provide get_search_summary")

        payload = self._repository.get_search_summary()
        if not isinstance(payload, dict):
            raise ContractQueryError("Repository returned invalid search summary payload")

        dataset_count = payload.get("active_dataset_count")
        source_count = payload.get("active_source_count")
        if not isinstance(dataset_count, int) or not isinstance(source_count, int):
            raise ContractQueryError("Repository returned invalid search summary counts")
        if dataset_count < 0 or source_count < 0:
            raise ContractQueryError("Repository returned negative search summary counts")

        return {
            "active_dataset_count": dataset_count,
            "active_source_count": source_count,
            "generated_at": payload.get("generated_at"),
        }

    def search_suggestions(
        self,
        *,
        query_text: str | None,
        limit: int | None,
    ) -> dict[str, Any]:
        """Return likely-match suggestions for current query text."""
        if not hasattr(self._repository, "search_suggestions"):
            raise ContractQueryError("Repository does not provide search_suggestions")

        normalized_query = normalize_query_text(query_text)
        if normalized_query is None:
            raise ContractQueryError("q must be provided")

        normalized_limit = DEFAULT_SUGGESTION_LIMIT if limit is None else limit
        if normalized_limit < MIN_SUGGESTION_LIMIT or normalized_limit > MAX_SUGGESTION_LIMIT:
            raise ContractQueryError(
                f"limit must be between {MIN_SUGGESTION_LIMIT} and {MAX_SUGGESTION_LIMIT}"
            )

        items = self._repository.search_suggestions(
            query_text=normalized_query,
            limit=normalized_limit,
        )
        if not isinstance(items, list):
            raise ContractQueryError("Repository returned invalid suggestions payload")

        projected: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                raise ContractQueryError("Repository returned invalid suggestion item")
            projected.append(
                {
                    "dataset_id": str(item.get("dataset_id", "")),
                    "source": deepcopy(item.get("source", {})),
                    "title": str(item.get("title", "")),
                    "rank_score": float(item.get("rank_score", 0.0)),
                }
            )

        return {
            "query": normalized_query,
            "limit": normalized_limit,
            "items": projected,
        }

    def list_recent_updates(self, *, limit: int | None) -> dict[str, Any]:
        """Return recent dataset updates payload."""
        if not hasattr(self._repository, "list_recent_datasets"):
            raise ContractQueryError("Repository does not provide list_recent_datasets")

        normalized_limit = normalize_recent_limit(limit)
        items = self._repository.list_recent_datasets(limit=normalized_limit)
        if not isinstance(items, list):
            raise ContractQueryError("Repository returned invalid recent updates payload")

        projected: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                raise ContractQueryError("Repository returned invalid recent updates item")

            dataset_id = str(item.get("dataset_id", "")).strip()
            if dataset_id == "":
                raise ContractQueryError("Repository returned recent item without dataset_id")

            source_value = item.get("source")
            source = deepcopy(source_value) if isinstance(source_value, dict) else {}
            source_id = str(source.get("id", "")).strip()
            source_name = str(source.get("name", "")).strip()
            if source_id == "" or source_name == "":
                raise ContractQueryError("Repository returned recent item without source")

            projected.append(
                {
                    "dataset_id": dataset_id,
                    "source": {
                        "id": source_id,
                        "name": source_name,
                    },
                    "title": str(item.get("title", "")).strip(),
                    "description": item.get("description")
                    if isinstance(item.get("description"), str) or item.get("description") is None
                    else str(item.get("description")),
                    "geographic_scope": item.get("geographic_scope")
                    if isinstance(item.get("geographic_scope"), str)
                    or item.get("geographic_scope") is None
                    else str(item.get("geographic_scope")),
                    "topic_tags": [str(tag) for tag in list(item.get("topic_tags") or [])],
                    "latest_update_at": item.get("latest_update_at"),
                    "action_links": {
                        "view_table_href": f"/datasets/{quote(dataset_id, safe='')}",
                        "download_csv_href": f"/api/datasets/{quote(dataset_id, safe='')}.csv",
                    },
                }
            )

        return {
            "items": projected,
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

        metadata_payload = deepcopy(metadata)
        metadata_fields = metadata_payload.get("metadata")
        if not isinstance(metadata_fields, dict):
            metadata_fields = {}

        unit_type = _resolve_dataset_unit_type(metadata_fields, observations)
        if unit_type is not None:
            metadata_fields["unit_type"] = unit_type
        metadata_payload["metadata"] = metadata_fields

        return {
            **metadata_payload,
            "observations": deepcopy(observations),
            "observation_sort": "observed_on_asc,reported_at_asc",
        }
