"""Runtime in-memory repository for dataset discovery HTTP endpoints."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any


class RuntimeDatasetDiscoveryRepository:
    """Deterministic repository used by the local backend HTTP API server."""

    def __init__(
        self,
        *,
        datasets: list[dict[str, Any]],
        observations: list[dict[str, Any]],
    ) -> None:
        """Initialize repository with deterministic dataset and observation rows."""
        self._datasets = datasets
        self._observations = observations

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
        latest: dict[str, str] = {}
        for row in self._observations:
            dataset_id = str(row.get("dataset_id", ""))
            if not dataset_id:
                continue
            reported_at = str(row.get("reported_at", ""))
            existing = latest.get(dataset_id)
            if existing is None or reported_at > existing:
                latest[dataset_id] = reported_at
        result: dict[str, str | None] = {}
        for row in self._datasets:
            dataset_id = str(row.get("dataset_id", ""))
            result[dataset_id] = latest.get(dataset_id)
        return result

    def _apply_search(
        self, *, query_text: str | None, source_id: str | None = None
    ) -> list[dict[str, Any]]:
        normalized = (query_text or "").strip().lower()
        latest = self._latest_update_by_dataset()
        rows: list[dict[str, Any]] = []
        for row in self._datasets:
            if source_id is not None:
                source_payload = row.get("source")
                source = source_payload if isinstance(source_payload, dict) else {}
                if str(source.get("id", "")) != source_id:
                    continue
            if normalized and normalized not in self._normalized_text(row):
                continue
            projected = dict(row)
            projected["latest_update_at"] = latest.get(str(row.get("dataset_id", "")))
            rows.append(projected)
        return rows

    @staticmethod
    def _paginate(
        rows: list[dict[str, Any]], *, page: int, page_size: int
    ) -> tuple[list[dict[str, Any]], int]:
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
        """Return datasets for landing page search."""
        rows = self._apply_search(query_text=query_text)
        rows.sort(
            key=lambda item: (
                str(item.get("latest_update_at", "") or ""),
                str(item.get("title", "")),
                str(item.get("dataset_id", "")),
            ),
            reverse=True,
        )
        return self._paginate(rows, page=page, page_size=page_size)

    def list_recent_datasets(self, *, limit: int) -> list[dict[str, Any]]:
        """Return at most ``limit`` datasets sorted by recency."""
        rows, _ = self.search_datasets(query_text=None, page=1, page_size=1000)
        return rows[:limit]

    def list_catalog_datasets(
        self,
        *,
        query_text: str | None,
        source_id: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict[str, Any]], int]:
        """Return filtered catalog rows sorted for deterministic browsing."""
        rows = self._apply_search(query_text=query_text, source_id=source_id)
        rows.sort(
            key=lambda item: (
                str((item.get("source") or {}).get("name", "")),
                str(item.get("title", "")),
                str(item.get("dataset_id", "")),
            )
        )
        return self._paginate(rows, page=page, page_size=page_size)

    def get_dataset_detail(self, *, dataset_id: str) -> dict[str, Any] | None:
        """Return one dataset metadata payload by canonical identifier."""
        for row in self._datasets:
            if str(row.get("dataset_id", "")) == dataset_id:
                return dict(row)
        return None

    def list_dataset_observations(
        self,
        *,
        dataset_id: str,
        from_date: date | None,
        to_date: date | None,
    ) -> list[dict[str, Any]]:
        """Return dataset observations filtered by optional date range."""
        rows = [row for row in self._observations if str(row.get("dataset_id", "")) == dataset_id]
        filtered: list[dict[str, Any]] = []
        for row in rows:
            observed = date.fromisoformat(str(row.get("observed_on")))
            if from_date is not None and observed < from_date:
                continue
            if to_date is not None and observed > to_date:
                continue
            projected = dict(row)
            projected["observed_on"] = observed.isoformat()
            filtered.append(projected)
        filtered.sort(
            key=lambda item: (str(item.get("observed_on", "")), str(item.get("reported_at", "")))
        )
        return filtered

    def group_catalog_by_source(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Group catalog rows by source for frontend organization."""
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            source_payload = row.get("source")
            source = source_payload if isinstance(source_payload, dict) else {}
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
