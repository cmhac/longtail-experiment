"""Postgres-backed repository for runtime dataset discovery reads."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping
from datetime import date, datetime
from typing import cast

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError


class PersistedDatasetDiscoveryRepository:
    """Read discovery/search/detail payloads from persisted Postgres records."""

    def __init__(self, *, engine: Engine) -> None:
        """Initialize repository with a SQLAlchemy engine."""
        self._engine = engine

    @staticmethod
    def _metadata_slug(value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
        return normalized or "unknown"

    @staticmethod
    def _iso_datetime(value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()

    @staticmethod
    def _iso_date(value: date | datetime | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date().isoformat()
        return value.isoformat()

    def _load_latest_summary_canonical_descriptors(self) -> dict[str, dict[str, object]]:
        """Return latest canonical descriptor projection keyed by dataset id."""
        query = text(
            """
            WITH ranked_descriptors AS (
                SELECT
                    ds.series_key AS dataset_id,
                    tcd.descriptor_state AS descriptor_state,
                    tcd.canonical_trend_label AS trend_label,
                    tcd.canonical_direction AS direction,
                    tcd.canonical_strength AS strength,
                    tcd.selected_lookback_points AS selected_lookback_points,
                    tcd.observed_on AS observed_on,
                    tcd.weighting_trace ->> 'reason_code' AS reason_code,
                    ROW_NUMBER() OVER (
                        PARTITION BY ds.series_key
                        ORDER BY tcd.observed_on DESC, tcd.created_at DESC
                    ) AS descriptor_rank
                FROM trend_canonical_descriptors tcd
                JOIN data_series ds ON ds.id = tcd.data_series_id
            )
            SELECT
                dataset_id,
                descriptor_state,
                trend_label,
                direction,
                strength,
                selected_lookback_points,
                observed_on,
                reason_code
            FROM ranked_descriptors
            WHERE descriptor_rank = 1
            """
        )
        with self._engine.connect() as connection:
            rows = connection.execute(query).mappings().all()

        descriptors: dict[str, dict[str, object]] = {}
        for row in rows:
            dataset_id = str(row["dataset_id"])
            observed_on = row["observed_on"]
            if isinstance(observed_on, (date, datetime)):
                observed_on_value = self._iso_date(cast(date | datetime | None, observed_on))
            else:
                observed_on_value = str(observed_on) if observed_on is not None else None
            descriptors[dataset_id] = {
                "descriptor_state": str(row["descriptor_state"]),
                "trend_label": (
                    str(row["trend_label"]) if row["trend_label"] is not None else None
                ),
                "direction": str(row["direction"]) if row["direction"] is not None else None,
                "strength": str(row["strength"]) if row["strength"] is not None else None,
                "selected_lookback_points": (
                    int(row["selected_lookback_points"])
                    if row["selected_lookback_points"] is not None
                    else None
                ),
                "observed_on": observed_on_value,
                "reason_code": (
                    str(row["reason_code"]) if row["reason_code"] is not None else None
                ),
            }
        return descriptors

    @staticmethod
    def _normalize_text(row: dict[str, object]) -> str:
        tags = cast(list[object], row.get("topic_tags") or [])
        tags_text = " ".join(str(tag) for tag in tags)
        source = cast(dict[str, object], row.get("source") or {})
        metadata = cast(dict[str, object], row.get("metadata") or {})
        return " ".join(
            [
                str(row.get("dataset_id", "")),
                str(row.get("title", "")),
                str(row.get("description", "")),
                str(row.get("geographic_scope", "")),
                str(source.get("id", "")),
                str(source.get("name", "")),
                str(metadata.get("metric_name", "")),
                tags_text,
            ]
        ).lower()

    def _load_dataset_rows(self) -> list[dict[str, object]]:
        summary_descriptors = self._load_latest_summary_canonical_descriptors()
        query = text(
            """
            SELECT
                ds.series_key AS dataset_id,
                sp.source_key AS source_key,
                sp.source_name AS source_name,
                sp.title AS source_title,
                sp.description AS source_description,
                sp.source_type AS source_type,
                ds.metric_name AS metric_name,
                ds.title AS title,
                ds.description AS description,
                ds.geographic_scope AS geographic_scope,
                COALESCE(
                    ARRAY_AGG(DISTINCT tt.tag_name ORDER BY tt.tag_name)
                        FILTER (WHERE tt.tag_name IS NOT NULL),
                    ARRAY[]::text[]
                ) AS topic_tags,
                MAX(o.reported_at) AS latest_update_at
            FROM data_series ds
            JOIN source_profiles sp ON sp.id = ds.source_profile_id
            LEFT JOIN data_series_topic_tags dstt ON dstt.data_series_id = ds.id
            LEFT JOIN topic_tags tt ON tt.id = dstt.topic_tag_id
            LEFT JOIN observations o ON o.series_id = ds.id
            GROUP BY
                ds.id,
                ds.series_key,
                sp.source_key,
                sp.source_name,
                sp.title,
                sp.description,
                sp.source_type,
                ds.metric_name,
                ds.title,
                ds.description,
                ds.geographic_scope
            """
        )
        with self._engine.connect() as connection:
            rows = connection.execute(query).mappings().all()

        projected: list[dict[str, object]] = []
        for row in rows:
            source_key = str(row["source_key"])
            source_title = str(row["source_title"])
            projected.append(
                {
                    "dataset_id": str(row["dataset_id"]),
                    "source": {
                        "id": source_key,
                        "name": source_title,
                    },
                    "title": str(row["title"]),
                    "description": (
                        str(row["description"]) if row["description"] is not None else None
                    ),
                    "geographic_scope": (
                        str(row["geographic_scope"])
                        if row["geographic_scope"] is not None
                        else None
                    ),
                    "topic_tags": [str(tag) for tag in (row["topic_tags"] or [])],
                    "latest_update_at": self._iso_datetime(row["latest_update_at"]),
                    "canonical_trend_descriptor": summary_descriptors.get(
                        str(row["dataset_id"]),
                        {
                            "descriptor_state": "unavailable",
                            "trend_label": None,
                            "direction": None,
                            "strength": None,
                            "selected_lookback_points": None,
                            "observed_on": None,
                            "reason_code": "missing_canonical_descriptor",
                        },
                    ),
                    "metadata": {
                        "metric_name": str(row["metric_name"]),
                        "source_key": source_key,
                        "source_name": str(row["source_name"]),
                        "source_title": source_title,
                        "source_description": str(row["source_description"]),
                        "source_type": str(row["source_type"]),
                    },
                }
            )
        return projected

    def _group_rows_by_source(
        self, rows: list[dict[str, object]]
    ) -> dict[tuple[str, str, str], list[dict[str, object]]]:
        grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
        for row in rows:
            source = row.get("source")
            source_payload: dict[str, object] = (
                cast(dict[str, object], source) if isinstance(source, dict) else {}
            )
            source_id = str(source_payload.get("id", ""))
            source_title = str(source_payload.get("name", ""))
            metadata = row.get("metadata")
            metadata_payload: dict[str, object] = (
                cast(dict[str, object], metadata) if isinstance(metadata, dict) else {}
            )
            source_description = str(metadata_payload.get("source_description", ""))
            grouped[(source_title, source_description, source_id)].append(row)
        return grouped

    def _match_topic_rows(self, *, topic_id: str) -> tuple[str, list[dict[str, object]]] | None:
        normalized_topic_id = topic_id.strip().lower()
        if normalized_topic_id == "":
            return None

        matches: list[tuple[str, dict[str, object]]] = []
        for row in self._load_dataset_rows():
            tags = [
                str(tag).strip()
                for tag in cast(list[object], row.get("topic_tags") or [])
                if str(tag).strip()
            ]
            matching_labels = [
                tag for tag in tags if self._metadata_slug(tag) == normalized_topic_id
            ]
            if not matching_labels:
                continue
            matches.append((sorted(matching_labels)[0], row))

        if not matches:
            return None

        topic_label = sorted({label for label, _ in matches})[0]
        rows = [dict(row) for label, row in matches if label == topic_label]
        return topic_label, rows

    def _match_geography_rows(
        self, *, geography_id: str
    ) -> tuple[str, list[dict[str, object]]] | None:
        normalized_geography_id = geography_id.strip().lower()
        if normalized_geography_id == "":
            return None

        matches: list[tuple[str, dict[str, object]]] = []
        for row in self._load_dataset_rows():
            geography_label = str(row.get("geographic_scope") or "").strip()
            if geography_label == "":
                continue
            if self._metadata_slug(geography_label) != normalized_geography_id:
                continue
            matches.append((geography_label, row))

        if not matches:
            return None

        geography_label = sorted({label for label, _ in matches})[0]
        rows = [dict(row) for label, row in matches if label == geography_label]
        return geography_label, rows

    @staticmethod
    def _paginate(
        rows: list[dict[str, object]], *, page: int, page_size: int
    ) -> tuple[list[dict[str, object]], int]:
        total_items = len(rows)
        start = (page - 1) * page_size
        end = start + page_size
        return rows[start:end], total_items

    def _apply_search(
        self,
        *,
        query_text: str | None,
        source_id: str | None,
        category: str | None = None,
    ) -> list[dict[str, object]]:
        normalized_query = (query_text or "").strip().lower()
        normalized_category = (category or "").strip().lower()
        rows = self._load_dataset_rows()
        filtered: list[dict[str, object]] = []
        for row in rows:
            if source_id is not None:
                source = row.get("source")
                source_payload: dict[str, object] = (
                    cast(dict[str, object], source) if isinstance(source, dict) else {}
                )
                if str(source_payload.get("id", "")) != source_id:
                    continue
            if normalized_category:
                topic_tags = [
                    str(tag).strip().lower()
                    for tag in cast(list[object], row.get("topic_tags") or [])
                ]
                if normalized_category not in topic_tags:
                    continue
            if normalized_query and normalized_query not in self._normalize_text(row):
                continue
            filtered.append(row)
        return filtered

    def search_datasets(
        self,
        *,
        query_text: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict[str, object]], int]:
        """Return paginated search rows sourced from persisted metadata."""
        rows = self._apply_search(query_text=query_text, source_id=None)
        rows.sort(
            key=lambda item: (
                str(item.get("latest_update_at", "") or ""),
                str(item.get("title", "")),
                str(item.get("dataset_id", "")),
            ),
            reverse=True,
        )
        return self._paginate(rows, page=page, page_size=page_size)

    def list_recent_datasets(self, *, limit: int) -> list[dict[str, object]]:
        """Return recent dataset summaries ordered by persisted recency."""
        rows, _ = self.search_datasets(query_text=None, page=1, page_size=1000)
        projected: list[dict[str, object]] = []
        for row in rows[:limit]:
            projected.append(
                {
                    "dataset_id": str(row.get("dataset_id", "")),
                    "source": dict(cast(dict[str, object], row.get("source") or {})),
                    "title": str(row.get("title", "")),
                    "description": row.get("description"),
                    "geographic_scope": row.get("geographic_scope"),
                    "topic_tags": list(cast(list[object], row.get("topic_tags") or [])),
                    "latest_update_at": row.get("latest_update_at"),
                    "canonical_trend_descriptor": dict(
                        cast(dict[str, object], row.get("canonical_trend_descriptor") or {})
                    ),
                }
            )
        return projected

    def list_recent_trend_events(self, *, limit: int) -> list[dict[str, object]]:
        """Return recent trend lifecycle events ordered by start period desc."""
        query = text(
            """
            SELECT
                ds.series_key AS dataset_id,
                sp.source_key AS source_key,
                sp.title AS source_title,
                ds.title AS title,
                tr.direction AS direction,
                tr.strength AS strength,
                tr.start_period AS start_period
            FROM trend_records tr
            JOIN data_series ds ON ds.id = tr.data_series_id
            JOIN source_profiles sp ON sp.id = ds.source_profile_id
            ORDER BY tr.start_period DESC, ds.series_key ASC
            LIMIT :limit
            """
        )
        with self._engine.connect() as connection:
            rows = connection.execute(query, {"limit": limit}).mappings().all()

        projected: list[dict[str, object]] = []
        for row in rows:
            start_period = self._iso_date(cast(date | datetime | None, row["start_period"]))
            if start_period is None:
                continue
            projected.append(
                {
                    "dataset_id": str(row["dataset_id"]),
                    "source": {
                        "id": str(row["source_key"]),
                        "name": str(row["source_title"]),
                    },
                    "title": str(row["title"]),
                    "direction": str(row["direction"]),
                    "strength": str(row["strength"]),
                    "start_period": start_period,
                }
            )
        return projected

    def get_search_summary(self) -> dict[str, object]:
        """Return active dataset and source totals for homepage summary text."""
        query = text(
            """
            SELECT
                COUNT(DISTINCT ds.series_key)::int AS active_dataset_count,
                COUNT(DISTINCT sp.source_key)::int AS active_source_count,
                CURRENT_TIMESTAMP AS generated_at
            FROM data_series ds
            JOIN source_profiles sp ON sp.id = ds.source_profile_id
            """
        )
        with self._engine.connect() as connection:
            row = connection.execute(query).mappings().one()

        return {
            "active_dataset_count": int(row["active_dataset_count"]),
            "active_source_count": int(row["active_source_count"]),
            "generated_at": self._iso_datetime(cast(datetime | None, row["generated_at"])),
        }

    def search_suggestions(
        self,
        *,
        query_text: str,
        limit: int,
    ) -> list[dict[str, object]]:
        """Return likely dataset matches using trigram ranking with stable ordering."""
        normalized_query = query_text.strip().lower()
        if not normalized_query:
            return []

        query = text(
            """
            SELECT
                ds.series_key AS dataset_id,
                sp.source_key AS source_key,
                sp.title AS source_title,
                ds.title AS title,
                GREATEST(
                    similarity(LOWER(ds.title), :query),
                    similarity(LOWER(ds.series_key), :query)
                ) AS rank_score
            FROM data_series ds
            JOIN source_profiles sp ON sp.id = ds.source_profile_id
            WHERE
                LOWER(ds.title) % :query
                OR LOWER(ds.series_key) % :query
                OR LOWER(ds.title) LIKE :query_like
                OR LOWER(ds.series_key) LIKE :query_like
            ORDER BY rank_score DESC, ds.title ASC, ds.series_key ASC
            LIMIT :limit
            """
        )

        try:
            with self._engine.connect() as connection:
                rows = (
                    connection.execute(
                        query,
                        {
                            "query": normalized_query,
                            "query_like": f"%{normalized_query}%",
                            "limit": limit,
                        },
                    )
                    .mappings()
                    .all()
                )
        except SQLAlchemyError:
            # Keep suggestions available even when trigram support is unavailable.
            rows = []
            for item in self._apply_search(query_text=normalized_query, source_id=None):
                rank = 1.0 if normalized_query in str(item.get("title", "")).lower() else 0.5
                rows.append(
                    {
                        "dataset_id": item.get("dataset_id", ""),
                        "source_key": cast(dict[str, object], item.get("source") or {}).get(
                            "id", ""
                        ),
                        "source_title": cast(dict[str, object], item.get("source") or {}).get(
                            "name", ""
                        ),
                        "title": item.get("title", ""),
                        "rank_score": rank,
                    }
                )
            rows.sort(
                key=lambda item: (
                    -float(item.get("rank_score", 0.0)),
                    str(item.get("title", "")),
                    str(item.get("dataset_id", "")),
                )
            )
            rows = rows[:limit]

        suggestions: list[dict[str, object]] = []
        for row in rows:
            source_key = str(row["source_key"])
            source_title = str(row["source_title"])
            suggestions.append(
                {
                    "dataset_id": str(row["dataset_id"]),
                    "source": {
                        "id": source_key,
                        "name": source_title,
                    },
                    "title": str(row["title"]),
                    "rank_score": float(row["rank_score"]),
                }
            )
        return suggestions

    def list_catalog_datasets(
        self,
        *,
        query_text: str | None,
        options: Mapping[str, object],
    ) -> tuple[list[dict[str, object]], int]:
        """Return paginated catalog rows with source and text filtering."""
        source_id = options.get("source_id")
        category = options.get("category")
        sort = str(options.get("sort", "recency")).strip().lower()
        raw_page = options.get("page")
        raw_page_size = options.get("page_size")
        page = raw_page if isinstance(raw_page, int) else 1
        page_size = raw_page_size if isinstance(raw_page_size, int) else 20
        normalized_source = source_id.strip() if isinstance(source_id, str) else None
        normalized_category = category.strip() if isinstance(category, str) else None
        if isinstance(normalized_source, str) and normalized_source.strip().lower() == "all":
            normalized_source = None
        if isinstance(normalized_category, str) and normalized_category.strip().lower() == "all":
            normalized_category = None

        rows = self._apply_search(
            query_text=query_text,
            source_id=normalized_source,
            category=normalized_category,
        )
        if sort == "title_asc":
            rows.sort(
                key=lambda item: (
                    str(item.get("title", "")),
                    str(item.get("dataset_id", "")),
                )
            )
        elif sort == "title_desc":
            rows.sort(
                key=lambda item: (
                    str(item.get("title", "")),
                    str(item.get("dataset_id", "")),
                ),
                reverse=True,
            )
        else:
            rows.sort(
                key=lambda item: (
                    str(item.get("latest_update_at", "") or ""),
                    str(item.get("title", "")),
                    str(item.get("dataset_id", "")),
                ),
                reverse=True,
            )
        return self._paginate(rows, page=page, page_size=page_size)

    def list_catalog_aggregations(self, *, query_text: str | None) -> dict[str, object]:
        """Return aggregate filter metadata across the current catalog scope."""
        rows = self._apply_search(query_text=query_text, source_id=None)
        grouped_sources = self._group_rows_by_source(rows)
        category_counts: dict[str, int] = defaultdict(int)

        for row in rows:
            tags = {
                str(tag).strip()
                for tag in cast(list[object], row.get("topic_tags") or [])
                if str(tag).strip()
            }
            for tag in tags:
                category_counts[tag] += 1

        return {
            "total_dataset_count": len(rows),
            "sources": [
                {
                    "source": {"id": source_id, "name": source_title},
                    "dataset_count": len(items),
                }
                for (source_title, _source_description, source_id), items in sorted(
                    grouped_sources.items()
                )
            ],
            "categories": [
                {"value": value, "dataset_count": count}
                for value, count in sorted(category_counts.items())
            ],
        }

    def list_sources(self) -> list[dict[str, object]]:
        """Return discoverable sources with dataset counts."""
        grouped = self._group_rows_by_source(self._load_dataset_rows())

        sources: list[dict[str, object]] = []
        for (source_title, source_description, source_id), items in sorted(grouped.items()):
            source_type: str | None = None
            if items:
                metadata = items[0].get("metadata")
                metadata_payload: dict[str, object] = (
                    cast(dict[str, object], metadata) if isinstance(metadata, dict) else {}
                )
                raw_source_type = metadata_payload.get("source_type")
                if isinstance(raw_source_type, str):
                    source_type = raw_source_type

            sources.append(
                {
                    "id": source_id,
                    "title": source_title,
                    "description": source_description,
                    "dataset_count": len(items),
                    "source_type": source_type,
                }
            )
        return sources

    def get_source_detail(
        self,
        *,
        source_id: str,
        page: int,
        page_size: int,
    ) -> dict[str, object] | None:
        """Return one source plus all of its discoverable datasets."""
        rows = self._apply_search(query_text=None, source_id=source_id)
        if not rows:
            return None

        rows.sort(
            key=lambda item: (
                str(item.get("title", "")),
                str(item.get("dataset_id", "")),
            )
        )
        source = rows[0].get("source")
        source_payload: dict[str, object] = (
            cast(dict[str, object], source) if isinstance(source, dict) else {}
        )
        metadata = rows[0].get("metadata")
        metadata_payload: dict[str, object] = (
            cast(dict[str, object], metadata) if isinstance(metadata, dict) else {}
        )
        raw_source_type = metadata_payload.get("source_type")
        paged_rows, total_items = self._paginate(rows, page=page, page_size=page_size)
        return {
            "source": {
                "id": str(source_payload.get("id", "")),
                "title": str(source_payload.get("name", "")),
                "description": str(metadata_payload.get("source_description", "")),
                "dataset_count": total_items,
                "source_type": str(raw_source_type) if isinstance(raw_source_type, str) else None,
            },
            "items": paged_rows,
            "total_items": total_items,
        }

    def get_topic_detail(
        self,
        *,
        topic_id: str,
        page: int,
        page_size: int,
    ) -> dict[str, object] | None:
        """Return one topic plus all of its discoverable datasets."""
        match = self._match_topic_rows(topic_id=topic_id)
        if match is None:
            return None

        topic_label, rows = match
        rows.sort(
            key=lambda item: (
                str(item.get("title", "")),
                str(item.get("dataset_id", "")),
            )
        )
        paged_rows, total_items = self._paginate(rows, page=page, page_size=page_size)
        return {
            "topic": {
                "id": self._metadata_slug(topic_label),
                "label": topic_label,
                "dataset_count": total_items,
            },
            "items": paged_rows,
            "total_items": total_items,
        }

    def get_geography_detail(
        self,
        *,
        geography_id: str,
        page: int,
        page_size: int,
    ) -> dict[str, object] | None:
        """Return one geography plus all of its discoverable datasets."""
        match = self._match_geography_rows(geography_id=geography_id)
        if match is None:
            return None

        geography_label, rows = match
        rows.sort(
            key=lambda item: (
                str(item.get("title", "")),
                str(item.get("dataset_id", "")),
            )
        )
        paged_rows, total_items = self._paginate(rows, page=page, page_size=page_size)
        return {
            "geography": {
                "id": self._metadata_slug(geography_label),
                "label": geography_label,
                "dataset_count": total_items,
            },
            "items": paged_rows,
            "total_items": total_items,
        }

    def get_dataset_detail(self, *, dataset_id: str) -> dict[str, object] | None:
        """Return one dataset metadata payload by canonical dataset id."""
        rows = self._load_dataset_rows()
        for row in rows:
            if str(row.get("dataset_id", "")) == dataset_id:
                return row
        return None

    def get_latest_dataset_canonical_trend_descriptor(
        self, *, dataset_id: str
    ) -> dict[str, object] | None:
        """Return latest canonical descriptor projected for dataset detail rendering."""
        query = text(
            """
            SELECT
                tcd.descriptor_state AS descriptor_state,
                tcd.canonical_trend_label AS trend_label,
                tcd.canonical_direction AS direction,
                tcd.canonical_strength AS strength,
                tcd.selected_lookback_points AS selected_lookback_points,
                tcd.observed_on AS observed_on,
                tcd.weighting_trace ->> 'reason_code' AS reason_code
            FROM trend_canonical_descriptors tcd
            JOIN data_series ds ON ds.id = tcd.data_series_id
            WHERE ds.series_key = :dataset_id
            ORDER BY tcd.observed_on DESC, tcd.created_at DESC
            LIMIT 1
            """
        )
        with self._engine.connect() as connection:
            rows = connection.execute(query, {"dataset_id": dataset_id}).mappings().all()
        if not rows:
            return None
        row = rows[0]
        observed_on = row["observed_on"]
        if isinstance(observed_on, (date, datetime)):
            observed_on_value = self._iso_date(cast(date | datetime | None, observed_on))
        else:
            observed_on_value = str(observed_on) if observed_on is not None else None
        return {
            "descriptor_state": str(row["descriptor_state"]),
            "trend_label": (str(row["trend_label"]) if row["trend_label"] is not None else None),
            "direction": str(row["direction"]) if row["direction"] is not None else None,
            "strength": str(row["strength"]) if row["strength"] is not None else None,
            "selected_lookback_points": (
                int(row["selected_lookback_points"])
                if row["selected_lookback_points"] is not None
                else None
            ),
            "observed_on": observed_on_value,
            "reason_code": (str(row["reason_code"]) if row["reason_code"] is not None else None),
        }

    def list_dataset_lookback_trend_snapshots(self, *, dataset_id: str) -> list[dict[str, object]]:
        """Return latest lookback evaluations and snapshots for dataset detail rendering."""
        query = text(
            """
            WITH latest_observation AS (
                SELECT
                    tcd.data_series_id,
                    tcd.observation_id
                FROM trend_canonical_descriptors tcd
                JOIN data_series ds ON ds.id = tcd.data_series_id
                WHERE ds.series_key = :dataset_id
                ORDER BY tcd.observed_on DESC, tcd.created_at DESC
                LIMIT 1
            )
            SELECT
                tle.lookback_points AS lookback_points,
                tle.applicability_state AS applicability_state,
                tls.outcome_state AS outcome_state,
                tls.trend_label AS trend_label,
                tls.direction AS direction,
                tls.strength AS strength,
                tle.reason_code AS reason_code
            FROM trend_lookback_evaluations tle
            JOIN latest_observation lo
                ON lo.data_series_id = tle.data_series_id
                AND lo.observation_id = tle.observation_id
            LEFT JOIN trend_lookback_snapshots tls
                ON tls.data_series_id = tle.data_series_id
                AND tls.observation_id = tle.observation_id
                AND tls.lookback_points = tle.lookback_points
            ORDER BY tle.lookback_points ASC
            """
        )
        with self._engine.connect() as connection:
            rows = connection.execute(query, {"dataset_id": dataset_id}).mappings().all()

        return [
            {
                "lookback_points": int(row["lookback_points"]),
                "applicability_state": str(row["applicability_state"]),
                "outcome_state": (
                    str(row["outcome_state"]) if row["outcome_state"] is not None else None
                ),
                "trend_label": (
                    str(row["trend_label"]) if row["trend_label"] is not None else None
                ),
                "direction": str(row["direction"]) if row["direction"] is not None else None,
                "strength": str(row["strength"]) if row["strength"] is not None else None,
                "reason_code": (
                    str(row["reason_code"]) if row["reason_code"] is not None else None
                ),
            }
            for row in rows
        ]

    def list_dataset_observations(
        self,
        *,
        dataset_id: str,
        from_date: date | None,
        to_date: date | None,
    ) -> list[dict[str, object]]:
        """Return chronological observation points for a dataset date range."""
        conditions = ["ds.series_key = :dataset_id"]
        query_params: dict[str, object] = {"dataset_id": dataset_id}
        if from_date is not None:
            conditions.append("o.observed_on >= :from_date")
            query_params["from_date"] = from_date
        if to_date is not None:
            conditions.append("o.observed_on <= :to_date")
            query_params["to_date"] = to_date

        where_clause = " AND ".join(conditions)
        query = text(
            f"""
            SELECT o.id, o.observed_on, o.value, o.reported_at, o.attributes
            FROM observations o
            JOIN data_series ds ON ds.id = o.series_id
            WHERE {where_clause}
            ORDER BY o.observed_on ASC, o.reported_at ASC
            """
        )
        with self._engine.connect() as connection:
            rows = connection.execute(query, query_params).mappings().all()

        candidate_query = text(
            """
            SELECT
                tcd.observed_on AS candidate_observed_on,
                candidate_observation.reported_at AS candidate_reported_at,
                tcd.created_at AS candidate_created_at,
                tcd.descriptor_state AS descriptor_state,
                tcd.canonical_trend_label AS trend_label,
                tcd.canonical_direction AS direction,
                tcd.canonical_strength AS strength,
                tcd.selected_lookback_points AS selected_lookback_points,
                tcd.weighting_trace ->> 'reason_code' AS reason_code
            FROM trend_canonical_descriptors tcd
            JOIN data_series ds ON ds.id = tcd.data_series_id
                        LEFT JOIN observations candidate_observation
                                ON candidate_observation.id = tcd.observation_id
            WHERE ds.series_key = :dataset_id
                            AND (
                                CAST(:from_date AS date) IS NULL
                                OR tcd.observed_on >= CAST(:from_date AS date)
                            )
                            AND (
                                CAST(:to_date AS date) IS NULL
                                OR tcd.observed_on <= CAST(:to_date AS date)
                            )
            ORDER BY
                tcd.observed_on ASC,
                candidate_observation.reported_at DESC NULLS LAST,
                tcd.created_at DESC
            """
        )
        with self._engine.connect() as connection:
            candidate_rows = (
                connection.execute(
                    candidate_query,
                    {
                        "dataset_id": dataset_id,
                        "from_date": from_date,
                        "to_date": to_date,
                    },
                )
                .mappings()
                .all()
            )

        candidates_by_observed_on: dict[str, list[dict[str, object]]] = defaultdict(list)
        for candidate_row in candidate_rows:
            candidate_observed_on = candidate_row["candidate_observed_on"]
            if isinstance(candidate_observed_on, (date, datetime)):
                observed_on_value = self._iso_date(
                    cast(date | datetime | None, candidate_observed_on)
                )
            else:
                observed_on_value = (
                    str(candidate_observed_on) if candidate_observed_on is not None else None
                )
            if observed_on_value is None:
                continue

            candidates_by_observed_on[observed_on_value].append(
                {
                    "descriptor_state": str(candidate_row["descriptor_state"]),
                    "trend_label": (
                        str(candidate_row["trend_label"])
                        if candidate_row["trend_label"] is not None
                        else None
                    ),
                    "direction": (
                        str(candidate_row["direction"])
                        if candidate_row["direction"] is not None
                        else None
                    ),
                    "strength": (
                        str(candidate_row["strength"])
                        if candidate_row["strength"] is not None
                        else None
                    ),
                    "selected_lookback_points": (
                        int(candidate_row["selected_lookback_points"])
                        if candidate_row["selected_lookback_points"] is not None
                        else None
                    ),
                    "observed_on": observed_on_value,
                    "reason_code": (
                        str(candidate_row["reason_code"])
                        if candidate_row["reason_code"] is not None
                        else None
                    ),
                    "_candidate_reported_at": self._iso_datetime(
                        cast(datetime | None, candidate_row["candidate_reported_at"])
                    )
                    if isinstance(candidate_row["candidate_reported_at"], datetime)
                    else (
                        str(candidate_row["candidate_reported_at"])
                        if candidate_row["candidate_reported_at"] is not None
                        else None
                    ),
                    "_candidate_created_at": self._iso_datetime(
                        cast(datetime | None, candidate_row["candidate_created_at"])
                    )
                    if isinstance(candidate_row["candidate_created_at"], datetime)
                    else (
                        str(candidate_row["candidate_created_at"])
                        if candidate_row["candidate_created_at"] is not None
                        else None
                    ),
                }
            )

        projected: list[dict[str, object]] = []
        for row in rows:
            observed_on = row["observed_on"]
            observed_on_value = (
                observed_on.isoformat()
                if isinstance(observed_on, (date, datetime))
                else str(observed_on)
            )
            reported_at_value = row["reported_at"]
            observation_reported_at = (
                self._iso_datetime(cast(datetime | None, reported_at_value))
                if isinstance(reported_at_value, datetime)
                else str(reported_at_value)
            )
            observation_reported_at_key = str(observation_reported_at or "")
            candidate_pool = candidates_by_observed_on.get(observed_on_value, [])
            observation_candidates = [
                candidate
                for candidate in candidate_pool
                if (
                    candidate.get("_candidate_reported_at") is None
                    or str(candidate.get("_candidate_reported_at") or "")
                    <= observation_reported_at_key
                )
            ]
            projected.append(
                {
                    "observed_on": observed_on_value,
                    "value": float(row["value"]),
                    "reported_at": observation_reported_at,
                    "attributes": dict(row["attributes"] or {}),
                    "as_of_trend_candidates": observation_candidates,
                }
            )
        return projected

    def group_catalog_by_source(self, rows: list[dict[str, object]]) -> list[dict[str, object]]:
        """Group catalog rows by source for grouped catalog responses."""
        grouped = self._group_rows_by_source(rows)

        groups: list[dict[str, object]] = []
        for (source_title, _source_description, source_id), items in sorted(grouped.items()):
            groups.append(
                {
                    "source": {"id": source_id, "name": source_title},
                    "dataset_count": len(items),
                    "dataset_ids": [str(item.get("dataset_id", "")) for item in items],
                }
            )
        return groups
