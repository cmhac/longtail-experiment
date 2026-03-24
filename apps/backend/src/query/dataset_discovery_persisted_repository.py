"""Postgres-backed repository for runtime dataset discovery reads."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date, datetime
from typing import cast

from sqlalchemy import Engine, text


class PersistedDatasetDiscoveryRepository:
    """Read discovery/search/detail payloads from persisted Postgres records."""

    def __init__(self, *, engine: Engine) -> None:
        """Initialize repository with a SQLAlchemy engine."""
        self._engine = engine

    @staticmethod
    def _source_id_from_name(source_name: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "-", source_name.lower()).strip("-")
        return normalized or "unknown"

    @staticmethod
    def _iso_datetime(value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()

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
        query = text(
            """
            SELECT
                ds.series_key AS dataset_id,
                sp.source_name AS source_name,
                sp.source_type AS source_type,
                sp.frequency_granularity AS frequency_granularity,
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
                sp.source_name,
                sp.source_type,
                sp.frequency_granularity,
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
            source_name = str(row["source_name"])
            projected.append(
                {
                    "dataset_id": str(row["dataset_id"]),
                    "source": {
                        "id": self._source_id_from_name(source_name),
                        "name": source_name,
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
                    "metadata": {
                        "metric_name": str(row["metric_name"]),
                        "source_type": str(row["source_type"]),
                        "frequency_granularity": str(row["frequency_granularity"]),
                    },
                }
            )
        return projected

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
    ) -> list[dict[str, object]]:
        normalized_query = (query_text or "").strip().lower()
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
        return rows[:limit]

    def list_catalog_datasets(
        self,
        *,
        query_text: str | None,
        source_id: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict[str, object]], int]:
        """Return paginated catalog rows with source and text filtering."""
        rows = self._apply_search(query_text=query_text, source_id=source_id)
        rows.sort(
            key=lambda item: (
                str((item.get("source") or {}).get("name", "")),
                str(item.get("title", "")),
                str(item.get("dataset_id", "")),
            )
        )
        return self._paginate(rows, page=page, page_size=page_size)

    def get_dataset_detail(self, *, dataset_id: str) -> dict[str, object] | None:
        """Return one dataset metadata payload by canonical dataset id."""
        rows = self._load_dataset_rows()
        for row in rows:
            if str(row.get("dataset_id", "")) == dataset_id:
                return row
        return None

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
            SELECT o.observed_on, o.value, o.reported_at, o.attributes
            FROM observations o
            JOIN data_series ds ON ds.id = o.series_id
            WHERE {where_clause}
            ORDER BY o.observed_on ASC, o.reported_at ASC
            """
        )
        with self._engine.connect() as connection:
            rows = connection.execute(query, query_params).mappings().all()

        projected: list[dict[str, object]] = []
        for row in rows:
            projected.append(
                {
                    "observed_on": row["observed_on"].isoformat(),
                    "value": float(row["value"]),
                    "reported_at": self._iso_datetime(row["reported_at"]),
                    "attributes": dict(row["attributes"] or {}),
                }
            )
        return projected

    def group_catalog_by_source(self, rows: list[dict[str, object]]) -> list[dict[str, object]]:
        """Group catalog rows by source for grouped catalog responses."""
        grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
        for row in rows:
            source = row.get("source")
            source_payload: dict[str, object] = (
                cast(dict[str, object], source) if isinstance(source, dict) else {}
            )
            source_id = str(source_payload.get("id", ""))
            source_name = str(source_payload.get("name", ""))
            grouped[(source_name, source_id)].append(row)

        groups: list[dict[str, object]] = []
        for (source_name, source_id), items in sorted(grouped.items()):
            groups.append(
                {
                    "source": {"id": source_id, "name": source_name},
                    "dataset_count": len(items),
                    "dataset_ids": [str(item.get("dataset_id", "")) for item in items],
                }
            )
        return groups
