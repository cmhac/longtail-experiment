"""In-memory repository for dataset discovery contract reads."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any, cast


class InMemoryDatasetDiscoveryRepository:
    """Provides deterministic search, catalog, and detail reads for tests."""

    def __init__(
        self,
        *,
        datasets: list[dict[str, object]] | None = None,
        observations: list[dict[str, object]] | None = None,
    ) -> None:
        self._datasets = list(datasets or [])
        self._observations = list(observations or [])

    @staticmethod
    def _normalized_text(row: dict[str, object]) -> str:
        raw_tags = row.get("topic_tags")
        tags = raw_tags if isinstance(raw_tags, list) else []
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
            current = latest.get(dataset_id)
            if current is None or reported_at > current:
                latest[dataset_id] = reported_at
        merged: dict[str, str | None] = {}
        for dataset in self._datasets:
            dataset_id = str(dataset.get("dataset_id", ""))
            merged[dataset_id] = latest.get(dataset_id)
        return merged

    def _apply_search(
        self, *, query_text: str | None, source_id: str | None = None
    ) -> list[dict[str, object]]:
        normalized = (query_text or "").strip().lower()
        rows: list[dict[str, object]] = []
        latest_update = self._latest_update_by_dataset()
        for row in self._datasets:
            if source_id is not None:
                source = row.get("source") or {}
                if str(source.get("id", "")) != source_id:
                    continue
            if normalized and normalized not in self._normalized_text(row):
                continue
            projected = dict(row)
            projected["latest_update_at"] = latest_update.get(
                str(row.get("dataset_id", ""))
            )
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
        rows: list[dict[str, object]], *, page: int, page_size: int
    ) -> tuple[list[dict[str, object]], int]:
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
    ) -> tuple[list[dict[str, object]], int]:
        """Return paginated datasets matching metadata and topic tags."""

        rows = self._apply_search(query_text=query_text)
        return self._paginate(rows, page=page, page_size=page_size)

    def list_recent_datasets(self, *, limit: int) -> list[dict[str, object]]:
        """Return top datasets by latest update timestamp."""

        rows = self._apply_search(query_text=None)
        return rows[:limit]

    def list_catalog_datasets(
        self,
        *,
        query_text: str | None,
        source_id: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict[str, object]], int]:
        """Return paginated catalog rows with optional source and text filters."""

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
        """Return full metadata for one dataset."""

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
    ) -> list[dict[str, object]]:
        """Return ordered observations for one dataset in optional date range."""

        rows = [
            row
            for row in self._observations
            if str(row.get("dataset_id", "")) == dataset_id
        ]

        def to_date_value(value: Any) -> date:
            if isinstance(value, date):
                return value
            return date.fromisoformat(str(value))

        filtered: list[dict[str, object]] = []
        for row in rows:
            observed_on = to_date_value(row.get("observed_on"))
            if from_date is not None and observed_on < from_date:
                continue
            if to_date is not None and observed_on > to_date:
                continue
            projected = dict(row)
            projected["observed_on"] = observed_on.isoformat()
            filtered.append(projected)

        filtered.sort(
            key=lambda item: (
                str(item.get("observed_on", "")),
                str(item.get("reported_at", "")),
            )
        )
        return filtered

    def group_catalog_by_source(
        self, rows: list[dict[str, object]]
    ) -> list[dict[str, object]]:
        """Group catalog rows by source preserving sorted source order."""

        grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
        for row in rows:
            raw_source = row.get("source")
            source: dict[str, object]
            if isinstance(raw_source, dict):
                source = cast(dict[str, object], raw_source)
            else:
                source = {}
            source_id = str(source.get("id", ""))
            source_name = str(source.get("name", ""))
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
