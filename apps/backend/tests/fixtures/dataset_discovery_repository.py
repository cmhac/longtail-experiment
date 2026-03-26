"""Test-only in-memory repository for dataset discovery contract fixtures."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any


class InMemoryDatasetDiscoveryRepository:
    """Provides deterministic data access behavior for backend contract tests."""

    def __init__(
        self,
        *,
        datasets: list[dict[str, Any]] | None = None,
        observations: list[dict[str, Any]] | None = None,
    ) -> None:
        """Initialize fixture rows for datasets and observations."""
        self._datasets = list(datasets or [])
        self._observations = list(observations or [])

    @staticmethod
    def _normalized_text(row: dict[str, Any]) -> str:
        tags = row.get("topic_tags") or []
        tags_text = " ".join(str(tag) for tag in tags)
        return " ".join(
            [
                str(row.get("title", "")),
                str(row.get("description", "")),
                str(row.get("geographic_scope", "")),
                tags_text,
            ]
        ).lower()

    def _latest_update_by_dataset(self) -> dict[str, str | None]:
        """Return latest reported timestamp for each dataset."""
        latest: dict[str, str] = {}
        for row in self._observations:
            dataset_id = str(row.get("dataset_id", ""))
            if not dataset_id:
                continue
            reported_at = str(row.get("reported_at", ""))
            current = latest.get(dataset_id)
            if current is None or reported_at > current:
                latest[dataset_id] = reported_at
        merged: dict[str, str | None] = {}
        for dataset in self._datasets:
            dataset_id = str(dataset.get("dataset_id", ""))
            merged[dataset_id] = latest.get(dataset_id)
        return merged

    def _apply_search(
        self,
        *,
        query_text: str | None,
        source_id: str | None = None,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        """Filter and project dataset rows for search-like queries."""
        normalized = (query_text or "").strip().lower()
        normalized_category = (category or "").strip().lower()
        rows: list[dict[str, Any]] = []
        latest_update = self._latest_update_by_dataset()
        for row in self._datasets:
            if source_id is not None:
                source = row.get("source") or {}
                if str(source.get("id", "")) != source_id:
                    continue
            if normalized_category:
                tags = [str(tag).strip().lower() for tag in (row.get("topic_tags") or [])]
                if normalized_category not in tags:
                    continue
            if normalized and normalized not in self._normalized_text(row):
                continue
            projected = dict(row)
            projected["latest_update_at"] = latest_update.get(str(row.get("dataset_id", "")))
            projected.setdefault("description", None)
            projected.setdefault("geographic_scope", None)
            projected.setdefault("topic_tags", [])
            rows.append(projected)
        rows.sort(
            key=lambda item: (
                str(item.get("latest_update_at", "") or ""),
                str(item.get("title", "")),
                str(item.get("dataset_id", "")),
            ),
            reverse=True,
        )
        return rows

    @staticmethod
    def _paginate(
        rows: list[dict[str, Any]], *, page: int, page_size: int
    ) -> tuple[list[dict[str, Any]], int]:
        """Return one page slice and total count."""
        total = len(rows)
        start = (page - 1) * page_size
        end = start + page_size
        return rows[start:end], total

    def search_datasets(
        self,
        *,
        query_text: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict[str, Any]], int]:
        """Return paged dataset search results."""
        rows = self._apply_search(query_text=query_text)
        return self._paginate(rows, page=page, page_size=page_size)

    def list_recent_datasets(self, *, limit: int) -> list[dict[str, Any]]:
        """Return most recently updated datasets up to limit."""
        rows = self._apply_search(query_text=None)
        return rows[:limit]

    def get_search_summary(self) -> dict[str, Any]:
        """Return aggregate dataset and source counts for homepage summary."""
        source_ids = {
            str((row.get("source") or {}).get("id", ""))
            for row in self._datasets
            if str((row.get("source") or {}).get("id", ""))
        }
        return {
            "active_dataset_count": len(self._datasets),
            "active_source_count": len(source_ids),
            "generated_at": "2026-03-24T00:00:00+00:00",
        }

    def search_suggestions(self, *, query_text: str, limit: int) -> list[dict[str, Any]]:
        """Return likely-match suggestions ranked by simple in-memory heuristics."""
        normalized = query_text.strip().lower()
        if not normalized:
            return []

        suggestions: list[dict[str, Any]] = []
        for row in self._datasets:
            dataset_id = str(row.get("dataset_id", ""))
            title = str(row.get("title", ""))
            haystack = f"{dataset_id} {title}".lower()
            if normalized not in haystack:
                continue
            score = 1.0 if normalized in title.lower() else 0.75
            suggestions.append(
                {
                    "dataset_id": dataset_id,
                    "source": dict(row.get("source") or {}),
                    "title": title,
                    "rank_score": score,
                }
            )

        suggestions.sort(
            key=lambda item: (
                -float(item.get("rank_score", 0.0)),
                str(item.get("title", "")),
                str(item.get("dataset_id", "")),
            )
        )
        return suggestions[:limit]

    def list_catalog_datasets(
        self,
        *,
        query_text: str | None,
        options: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], int]:
        """Return paged catalog rows sorted by source and title."""
        source_id = options.get("source_id")
        category = options.get("category")
        sort = str(options.get("sort", "recency"))
        page = int(options.get("page", 1))
        page_size = int(options.get("page_size", 20))

        rows = self._apply_search(
            query_text=query_text,
            source_id=source_id if isinstance(source_id, str) else None,
            category=category if isinstance(category, str) else None,
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

    def list_catalog_aggregations(self, *, query_text: str | None) -> dict[str, Any]:
        """Return aggregate filter metadata across the catalog scope."""
        rows = self._apply_search(query_text=query_text)
        source_counts: dict[tuple[str, str], int] = {}
        category_counts: dict[str, int] = {}

        for row in rows:
            source = row.get("source") or {}
            source_id = str(source.get("id", "")).strip()
            source_name = str(source.get("name", "")).strip()
            if source_id and source_name:
                key = (source_name, source_id)
                source_counts[key] = source_counts.get(key, 0) + 1

            tags = {str(tag).strip() for tag in (row.get("topic_tags") or []) if str(tag).strip()}
            for tag in tags:
                category_counts[tag] = category_counts.get(tag, 0) + 1

        return {
            "total_dataset_count": len(rows),
            "sources": [
                {
                    "source": {"id": source_id, "name": source_name},
                    "dataset_count": count,
                }
                for (source_name, source_id), count in sorted(source_counts.items())
            ],
            "categories": [
                {"value": value, "dataset_count": count}
                for value, count in sorted(category_counts.items())
            ],
        }

    def get_dataset_detail(self, *, dataset_id: str) -> dict[str, Any] | None:
        """Return one dataset by identifier when available."""
        for row in self._datasets:
            if str(row.get("dataset_id", "")) == dataset_id:
                return dict(row)
        return None

    def list_sources(self) -> list[dict[str, Any]]:
        """Return unique sources with dataset counts."""
        grouped: dict[tuple[str, str], dict[str, Any]] = {}
        for row in self._datasets:
            source = row.get("source") or {}
            source_id = str(source.get("id", "")).strip()
            source_name = str(source.get("name", "")).strip()
            if not source_id or not source_name:
                continue
            key = (source_name, source_id)
            entry = grouped.setdefault(
                key,
                {
                    "id": source_id,
                    "name": source_name,
                    "dataset_count": 0,
                    "source_type": (row.get("metadata") or {}).get("source_type"),
                },
            )
            entry["dataset_count"] += 1

        return [grouped[key] for key in sorted(grouped)]

    def get_source_detail(self, *, source_id: str) -> dict[str, Any] | None:
        """Return one source summary plus its datasets."""
        datasets = self._apply_search(query_text=None, source_id=source_id)
        if not datasets:
            return None

        source = dict(datasets[0].get("source") or {})
        metadata = dict(datasets[0].get("metadata") or {})
        datasets.sort(
            key=lambda item: (
                str(item.get("title", "")),
                str(item.get("dataset_id", "")),
            )
        )
        return {
            "source": {
                "id": str(source.get("id", "")),
                "name": str(source.get("name", "")),
                "dataset_count": len(datasets),
                "source_type": metadata.get("source_type"),
            },
            "datasets": datasets,
        }

    def list_dataset_observations(
        self,
        *,
        dataset_id: str,
        from_date: date | None,
        to_date: date | None,
    ) -> list[dict[str, Any]]:
        """Return observations for one dataset with optional date bounds."""
        rows = [row for row in self._observations if str(row.get("dataset_id", "")) == dataset_id]

        filtered: list[dict[str, Any]] = []
        for row in rows:
            observed_on = date.fromisoformat(str(row.get("observed_on")))
            if from_date is not None and observed_on < from_date:
                continue
            if to_date is not None and observed_on > to_date:
                continue
            projected = dict(row)
            projected["observed_on"] = observed_on.isoformat()
            filtered.append(projected)

        filtered.sort(
            key=lambda item: (str(item.get("observed_on", "")), str(item.get("reported_at", "")))
        )
        return filtered

    def group_catalog_by_source(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Group catalog rows by source metadata for contract assertions."""
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            source = row.get("source") or {}
            source_id = str(source.get("id", ""))
            source_name = str(source.get("name", ""))
            grouped[(source_name, source_id)].append(row)

        groups: list[dict[str, Any]] = []
        for (source_name, source_id), items in sorted(grouped.items()):
            groups.append(
                {
                    "source": {"id": source_id, "name": source_name},
                    "dataset_count": len(items),
                    "dataset_ids": [str(item.get("dataset_id", "")) for item in items],
                }
            )
        return groups
