"""Service orchestration for dataset discovery query workflows."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any
from urllib.parse import quote

from pydantic import ValidationError

from src.contract.errors import ContractQueryError
from src.contract.query.dataset_detail_query import (
    CanonicalTrendDescriptor,
    LookbackTrendSnapshot,
)
from src.contract.query.dataset_search_query import SummaryCanonicalTrendDescriptor

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
CATALOG_SORT_KEYS = {
    "recency": "latest_update_at_desc,title_asc,dataset_id_asc",
    "title_asc": "title_asc,dataset_id_asc",
    "title_desc": "title_desc,dataset_id_desc",
}


def _normalize_catalog_filter_value(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if normalized == "" or normalized.lower() == "all":
        return None
    return normalized


# Discovery pagination rollout checklist: keep metadata fields and semantics
# consistent across all list routes as pagination support expands.


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


def _build_paginated_payload(
    *,
    items: list[dict[str, Any]],
    page: int,
    page_size: int,
    total_items: int,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a consistent pagination envelope for discovery list responses."""
    total_pages = ((total_items - 1) // page_size + 1) if total_items else 0
    payload: dict[str, Any] = {
        "items": deepcopy(items),
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
    }
    if extra:
        payload.update(deepcopy(dict(extra)))
    return payload


def _default_summary_canonical_descriptor() -> dict[str, Any]:
    return {
        "descriptor_state": "unavailable",
        "trend_label": None,
        "direction": None,
        "strength": None,
        "selected_lookback_points": None,
        "observed_on": None,
        "reason_code": "missing_canonical_descriptor",
    }


def _resolve_summary_canonical_descriptor(
    *, raw_descriptor: object, dataset_id: str
) -> dict[str, Any]:
    payload = (
        raw_descriptor
        if isinstance(raw_descriptor, dict)
        else _default_summary_canonical_descriptor()
    )
    try:
        return SummaryCanonicalTrendDescriptor.model_validate(payload).model_dump()
    except (ValidationError, TypeError, ValueError) as exc:
        raise ContractQueryError(
            f"dataset_summary_canonical_payload_invalid:{dataset_id}"
        ) from exc


def _project_dataset_summary_item(item: dict[str, Any]) -> dict[str, Any]:
    dataset_id = str(item.get("dataset_id", "")).strip()
    return {
        "dataset_id": dataset_id,
        "source": deepcopy(item.get("source", {})),
        "title": str(item.get("title", "")).strip(),
        "description": item.get("description")
        if isinstance(item.get("description"), str) or item.get("description") is None
        else str(item.get("description")),
        "geographic_scope": item.get("geographic_scope")
        if isinstance(item.get("geographic_scope"), str) or item.get("geographic_scope") is None
        else str(item.get("geographic_scope")),
        "topic_tags": [str(tag) for tag in list(item.get("topic_tags") or [])],
        "latest_update_at": item.get("latest_update_at"),
        "canonical_trend_descriptor": _resolve_summary_canonical_descriptor(
            raw_descriptor=item.get("canonical_trend_descriptor"),
            dataset_id=dataset_id,
        ),
    }


def _project_recent_trend_items(
    *,
    repository: Any,
    normalized_limit: int,
) -> list[dict[str, Any]]:
    if not hasattr(repository, "list_recent_trend_events"):
        return []

    trend_items = repository.list_recent_trend_events(limit=normalized_limit)
    if not isinstance(trend_items, list):
        raise ContractQueryError("Repository returned invalid recent trend payload")

    trend_projected: list[dict[str, Any]] = []
    for item in trend_items:
        if not isinstance(item, dict):
            raise ContractQueryError("Repository returned invalid recent trend item")

        dataset_id = str(item.get("dataset_id", "")).strip()
        if dataset_id == "":
            raise ContractQueryError("Repository returned trend item without dataset_id")

        source_value = item.get("source")
        source = deepcopy(source_value) if isinstance(source_value, dict) else {}
        source_id = str(source.get("id", "")).strip()
        source_name = str(source.get("name", "")).strip()
        if source_id == "" or source_name == "":
            raise ContractQueryError("Repository returned trend item without source")

        start_period = item.get("start_period")
        if not isinstance(start_period, str) or start_period.strip() == "":
            raise ContractQueryError("Repository returned trend item without start_period")

        trend_projected.append(
            {
                "item_type": "trend_event",
                "dataset_id": dataset_id,
                "source": {
                    "id": source_id,
                    "name": source_name,
                },
                "title": str(item.get("title", "")).strip(),
                "direction": str(item.get("direction", "")).strip().lower(),
                "strength": str(item.get("strength", "")).strip().lower(),
                "start_period": start_period,
                "latest_update_at": start_period,
                "action_links": {
                    "view_table_href": f"/datasets/{quote(dataset_id, safe='')}",
                    "download_csv_href": f"/api/datasets/{quote(dataset_id, safe='')}.csv",
                },
            }
        )
    return trend_projected


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
                "list_catalog_aggregations",
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
        if total_pages > 0 and normalized_page > total_pages:
            normalized_page = total_pages
            items, total_items = self._repository.search_datasets(
                query_text=normalized_query,
                page=normalized_page,
                page_size=normalized_page_size,
            )
            if not isinstance(items, list) or not isinstance(total_items, int):
                raise ContractQueryError("Repository returned invalid search payload")
        projected = [
            _project_dataset_summary_item(item)
            for item in items
            if isinstance(item, dict)
        ]
        if len(projected) != len(items):
            raise ContractQueryError("Repository returned invalid search item")
        return _build_paginated_payload(
            items=projected,
            page=normalized_page,
            page_size=normalized_page_size,
            total_items=total_items,
            extra={
                "sort": "latest_update_at_desc,title_asc,dataset_id_asc",
            },
        )

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

            canonical_trend_descriptor = _resolve_summary_canonical_descriptor(
                raw_descriptor=item.get("canonical_trend_descriptor"),
                dataset_id=dataset_id,
            )
            projected.append(
                {
                    "item_type": "dataset_update",
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
                    "canonical_trend_descriptor": canonical_trend_descriptor,
                    "action_links": {
                        "view_table_href": f"/datasets/{quote(dataset_id, safe='')}",
                        "download_csv_href": f"/api/datasets/{quote(dataset_id, safe='')}.csv",
                    },
                }
            )

        trend_projected = _project_recent_trend_items(
            repository=self._repository,
            normalized_limit=normalized_limit,
        )

        merged_items = projected + trend_projected
        merged_items.sort(
            key=lambda item: (
                str(item.get("latest_update_at", "") or ""),
                str(item.get("title", "")),
                str(item.get("dataset_id", "")),
            ),
            reverse=True,
        )

        return {
            "items": merged_items[:normalized_limit],
            "limit": normalized_limit,
            "sort": "event_timestamp_desc,title_asc,dataset_id_asc",
        }

    def list_catalog(
        self,
        *,
        query_text: str | None,
        options: Mapping[str, object] | None,
        group_by_source: bool,
    ) -> dict[str, Any]:
        """Return catalog results with optional source grouping."""
        if not hasattr(self._repository, "list_catalog_datasets"):
            raise ContractQueryError("Repository does not provide list_catalog_datasets")

        catalog_options = options or {}
        normalized_query = normalize_query_text(query_text)
        raw_page = catalog_options.get("page")
        raw_page_size = catalog_options.get("page_size")
        raw_source = catalog_options.get("source_id")
        raw_category = catalog_options.get("category")
        raw_sort = catalog_options.get("sort")

        normalized_page = normalize_page(raw_page if isinstance(raw_page, int) else None)
        normalized_page_size = normalize_page_size(
            raw_page_size if isinstance(raw_page_size, int) else None
        )
        normalized_source = _normalize_catalog_filter_value(raw_source)
        normalized_category = _normalize_catalog_filter_value(raw_category)
        normalized_sort = (
            raw_sort.strip().lower()
            if isinstance(raw_sort, str) and raw_sort.strip()
            else "recency"
        )
        if normalized_sort not in CATALOG_SORT_KEYS:
            normalized_sort = "recency"

        items, total_items = self._repository.list_catalog_datasets(
            query_text=normalized_query,
            options={
                "source_id": normalized_source,
                "category": normalized_category,
                "sort": normalized_sort,
                "page": normalized_page,
                "page_size": normalized_page_size,
            },
        )
        if not isinstance(items, list) or not isinstance(total_items, int):
            raise ContractQueryError("Repository returned invalid catalog payload")
        total_pages = ((total_items - 1) // normalized_page_size + 1) if total_items else 0
        if total_pages > 0 and normalized_page > total_pages:
            normalized_page = total_pages
            items, total_items = self._repository.list_catalog_datasets(
                query_text=normalized_query,
                options={
                    "source_id": normalized_source,
                    "category": normalized_category,
                    "sort": normalized_sort,
                    "page": normalized_page,
                    "page_size": normalized_page_size,
                },
            )
            if not isinstance(items, list) or not isinstance(total_items, int):
                raise ContractQueryError("Repository returned invalid catalog payload")
        projected = [
            _project_dataset_summary_item(item)
            for item in items
            if isinstance(item, dict)
        ]
        if len(projected) != len(items):
            raise ContractQueryError("Repository returned invalid catalog item")
        aggregations = self._repository.list_catalog_aggregations(query_text=normalized_query)
        if not isinstance(aggregations, dict):
            raise ContractQueryError("Repository returned invalid catalog aggregations payload")

        groups: list[dict[str, Any]] = []
        if group_by_source and hasattr(self._repository, "group_catalog_by_source"):
            groups = self._repository.group_catalog_by_source(projected)
            if not isinstance(groups, list):
                raise ContractQueryError("Repository returned invalid source grouping payload")

        return _build_paginated_payload(
            items=projected,
            page=normalized_page,
            page_size=normalized_page_size,
            total_items=total_items,
            extra={
                "sort": CATALOG_SORT_KEYS[normalized_sort],
                "groups": groups,
                "aggregations": aggregations,
            },
        )

    def list_sources(self) -> dict[str, Any]:
        """Return discoverable sources with dataset counts."""
        if not hasattr(self._repository, "list_sources"):
            raise ContractQueryError("Repository does not provide list_sources")

        items = self._repository.list_sources()
        if not isinstance(items, list):
            raise ContractQueryError("Repository returned invalid source list payload")

        projected: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                raise ContractQueryError("Repository returned invalid source list item")

            source_id = str(item.get("id", "")).strip()
            source_title = str(item.get("title", "")).strip()
            source_description = str(item.get("description", "")).strip()
            dataset_count = item.get("dataset_count")
            if source_id == "" or source_title == "" or source_description == "":
                raise ContractQueryError(
                    "Repository returned source without id, title, or description"
                )
            if not isinstance(dataset_count, int) or dataset_count < 0:
                raise ContractQueryError("Repository returned invalid source dataset_count")

            projected.append(
                {
                    "id": source_id,
                    "title": source_title,
                    "description": source_description,
                    "dataset_count": dataset_count,
                    "source_type": (
                        str(item.get("source_type"))
                        if isinstance(item.get("source_type"), str)
                        else None
                    ),
                }
            )

        return {
            "items": projected,
            "total_items": len(projected),
            "sort": "source_title_asc,source_id_asc",
        }

    def get_source_detail(
        self,
        *,
        source_id: str,
        page: int | None,
        page_size: int | None,
    ) -> dict[str, Any]:
        """Return one source plus its attributed datasets."""
        if not hasattr(self._repository, "get_source_detail"):
            raise ContractQueryError("Repository does not provide get_source_detail")

        normalized_source_id = source_id.strip()
        if not normalized_source_id:
            raise ContractQueryError("source_id must be provided")

        normalized_page = normalize_page(page)
        normalized_page_size = normalize_page_size(page_size)
        payload = self._repository.get_source_detail(
            source_id=normalized_source_id,
            page=normalized_page,
            page_size=normalized_page_size,
        )
        if payload is None:
            raise ContractQueryError("source_not_found")
        if not isinstance(payload, dict):
            raise ContractQueryError("Repository returned invalid source detail payload")

        source = payload.get("source")
        items = payload.get("items")
        total_items = payload.get("total_items")
        if not isinstance(source, dict) or not isinstance(items, list):
            raise ContractQueryError("Repository returned invalid source detail payload")
        if not isinstance(total_items, int) or total_items < 0:
            raise ContractQueryError("Repository returned invalid source total_items")

        total_pages = ((total_items - 1) // normalized_page_size + 1) if total_items else 0
        if total_pages > 0 and normalized_page > total_pages:
            normalized_page = total_pages
            payload = self._repository.get_source_detail(
                source_id=normalized_source_id,
                page=normalized_page,
                page_size=normalized_page_size,
            )
            if payload is None or not isinstance(payload, dict):
                raise ContractQueryError("Repository returned invalid source detail payload")
            source = payload.get("source")
            items = payload.get("items")
            total_items = payload.get("total_items")
            if not isinstance(source, dict) or not isinstance(items, list):
                raise ContractQueryError("Repository returned invalid source detail payload")
            if not isinstance(total_items, int) or total_items < 0:
                raise ContractQueryError("Repository returned invalid source total_items")

        dataset_count = source.get("dataset_count")
        if not isinstance(dataset_count, int) or dataset_count < 0:
            raise ContractQueryError("Repository returned invalid source dataset_count")
        projected = [
            _project_dataset_summary_item(item)
            for item in items
            if isinstance(item, dict)
        ]
        if len(projected) != len(items):
            raise ContractQueryError("Repository returned invalid source detail item")

        return _build_paginated_payload(
            items=projected,
            page=normalized_page,
            page_size=normalized_page_size,
            total_items=total_items,
            extra={
                "sort": "title_asc,dataset_id_asc",
                "source": {
                    "id": str(source.get("id", "")).strip(),
                    "title": str(source.get("title", "")).strip(),
                    "description": str(source.get("description", "")).strip(),
                    "dataset_count": dataset_count,
                    "source_type": (
                        str(source.get("source_type"))
                        if isinstance(source.get("source_type"), str)
                        else None
                    ),
                },
            },
        )

    def get_topic_detail(
        self,
        *,
        topic_id: str,
        page: int | None,
        page_size: int | None,
    ) -> dict[str, Any]:
        """Return one topic plus its attributed datasets."""
        if not hasattr(self._repository, "get_topic_detail"):
            raise ContractQueryError("Repository does not provide get_topic_detail")

        normalized_topic_id = topic_id.strip()
        if not normalized_topic_id:
            raise ContractQueryError("topic_id must be provided")

        normalized_page = normalize_page(page)
        normalized_page_size = normalize_page_size(page_size)
        payload = self._repository.get_topic_detail(
            topic_id=normalized_topic_id,
            page=normalized_page,
            page_size=normalized_page_size,
        )
        if payload is None:
            raise ContractQueryError("topic_not_found")
        if not isinstance(payload, dict):
            raise ContractQueryError("Repository returned invalid topic detail payload")

        topic = payload.get("topic")
        items = payload.get("items")
        total_items = payload.get("total_items")
        if not isinstance(topic, dict) or not isinstance(items, list):
            raise ContractQueryError("Repository returned invalid topic detail payload")
        if not isinstance(total_items, int) or total_items < 0:
            raise ContractQueryError("Repository returned invalid topic total_items")

        total_pages = ((total_items - 1) // normalized_page_size + 1) if total_items else 0
        if total_pages > 0 and normalized_page > total_pages:
            normalized_page = total_pages
            payload = self._repository.get_topic_detail(
                topic_id=normalized_topic_id,
                page=normalized_page,
                page_size=normalized_page_size,
            )
            if payload is None or not isinstance(payload, dict):
                raise ContractQueryError("Repository returned invalid topic detail payload")
            topic = payload.get("topic")
            items = payload.get("items")
            total_items = payload.get("total_items")
            if not isinstance(topic, dict) or not isinstance(items, list):
                raise ContractQueryError("Repository returned invalid topic detail payload")
            if not isinstance(total_items, int) or total_items < 0:
                raise ContractQueryError("Repository returned invalid topic total_items")

        dataset_count = topic.get("dataset_count")
        if not isinstance(dataset_count, int) or dataset_count < 0:
            raise ContractQueryError("Repository returned invalid topic dataset_count")
        projected = [
            _project_dataset_summary_item(item)
            for item in items
            if isinstance(item, dict)
        ]
        if len(projected) != len(items):
            raise ContractQueryError("Repository returned invalid topic detail item")

        return _build_paginated_payload(
            items=projected,
            page=normalized_page,
            page_size=normalized_page_size,
            total_items=total_items,
            extra={
                "sort": "title_asc,dataset_id_asc",
                "topic": {
                    "id": str(topic.get("id", "")).strip(),
                    "label": str(topic.get("label", "")).strip(),
                    "dataset_count": dataset_count,
                },
            },
        )

    def get_geography_detail(
        self,
        *,
        geography_id: str,
        page: int | None,
        page_size: int | None,
    ) -> dict[str, Any]:
        """Return one geography plus its attributed datasets."""
        if not hasattr(self._repository, "get_geography_detail"):
            raise ContractQueryError("Repository does not provide get_geography_detail")

        normalized_geography_id = geography_id.strip()
        if not normalized_geography_id:
            raise ContractQueryError("geography_id must be provided")

        normalized_page = normalize_page(page)
        normalized_page_size = normalize_page_size(page_size)
        payload = self._repository.get_geography_detail(
            geography_id=normalized_geography_id,
            page=normalized_page,
            page_size=normalized_page_size,
        )
        if payload is None:
            raise ContractQueryError("geography_not_found")
        if not isinstance(payload, dict):
            raise ContractQueryError("Repository returned invalid geography detail payload")

        geography = payload.get("geography")
        items = payload.get("items")
        total_items = payload.get("total_items")
        if not isinstance(geography, dict) or not isinstance(items, list):
            raise ContractQueryError("Repository returned invalid geography detail payload")
        if not isinstance(total_items, int) or total_items < 0:
            raise ContractQueryError("Repository returned invalid geography total_items")

        total_pages = ((total_items - 1) // normalized_page_size + 1) if total_items else 0
        if total_pages > 0 and normalized_page > total_pages:
            normalized_page = total_pages
            payload = self._repository.get_geography_detail(
                geography_id=normalized_geography_id,
                page=normalized_page,
                page_size=normalized_page_size,
            )
            if payload is None or not isinstance(payload, dict):
                raise ContractQueryError("Repository returned invalid geography detail payload")
            geography = payload.get("geography")
            items = payload.get("items")
            total_items = payload.get("total_items")
            if not isinstance(geography, dict) or not isinstance(items, list):
                raise ContractQueryError("Repository returned invalid geography detail payload")
            if not isinstance(total_items, int) or total_items < 0:
                raise ContractQueryError("Repository returned invalid geography total_items")

        dataset_count = geography.get("dataset_count")
        if not isinstance(dataset_count, int) or dataset_count < 0:
            raise ContractQueryError("Repository returned invalid geography dataset_count")
        projected = [
            _project_dataset_summary_item(item)
            for item in items
            if isinstance(item, dict)
        ]
        if len(projected) != len(items):
            raise ContractQueryError("Repository returned invalid geography detail item")

        return _build_paginated_payload(
            items=projected,
            page=normalized_page,
            page_size=normalized_page_size,
            total_items=total_items,
            extra={
                "sort": "title_asc,dataset_id_asc",
                "geography": {
                    "id": str(geography.get("id", "")).strip(),
                    "label": str(geography.get("label", "")).strip(),
                    "dataset_count": dataset_count,
                },
            },
        )

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

        canonical_descriptor = self._resolve_canonical_descriptor(dataset_id=normalized_dataset_id)
        lookback_snapshots = self._resolve_lookback_snapshots(dataset_id=normalized_dataset_id)

        return {
            **metadata_payload,
            "observations": deepcopy(observations),
            "canonical_trend_descriptor": canonical_descriptor,
            "lookback_trend_snapshots": lookback_snapshots,
            "observation_sort": "observed_on_asc,reported_at_asc",
        }

    def _resolve_canonical_descriptor(self, *, dataset_id: str) -> dict[str, Any]:
        descriptor = CanonicalTrendDescriptor(
            descriptor_state="unavailable",
            trend_label=None,
            direction=None,
            strength=None,
            selected_lookback_points=None,
            observed_on=None,
            reason_code="missing_canonical_descriptor",
        ).model_dump()
        if not hasattr(self._repository, "get_latest_dataset_canonical_trend_descriptor"):
            return descriptor

        raw_canonical = self._repository.get_latest_dataset_canonical_trend_descriptor(
            dataset_id=dataset_id
        )
        if raw_canonical is None:
            return descriptor
        if not isinstance(raw_canonical, dict):
            raise ContractQueryError("dataset_detail_canonical_payload_invalid")

        try:
            return CanonicalTrendDescriptor.model_validate(raw_canonical).model_dump()
        except (ValidationError, TypeError, ValueError) as exc:
            raise ContractQueryError("dataset_detail_canonical_payload_invalid") from exc

    def _resolve_lookback_snapshots(self, *, dataset_id: str) -> list[dict[str, Any]]:
        if not hasattr(self._repository, "list_dataset_lookback_trend_snapshots"):
            return []

        raw_lookbacks = self._repository.list_dataset_lookback_trend_snapshots(
            dataset_id=dataset_id
        )
        if not isinstance(raw_lookbacks, list):
            raise ContractQueryError("dataset_detail_lookback_snapshot_payload_invalid")
        if not all(isinstance(snapshot, dict) for snapshot in raw_lookbacks):
            raise ContractQueryError("dataset_detail_lookback_snapshot_payload_invalid")

        try:
            return [
                LookbackTrendSnapshot.model_validate(snapshot).model_dump()
                for snapshot in raw_lookbacks
            ]
        except (ValidationError, TypeError, ValueError) as exc:
            raise ContractQueryError("dataset_detail_lookback_snapshot_payload_invalid") from exc
