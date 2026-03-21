"""Backend canonical observation query projection service."""

from __future__ import annotations

from typing import Any

from src.contract.errors import ContractQueryError


class CanonicalObservationQueryService:
    """Reads canonical observation rows from shared repositories."""

    def __init__(self, repository: Any) -> None:
        """Initialize query service with a repository dependency."""
        self._repository = repository

    def _list_rows(self) -> list[dict[str, object]]:
        if not hasattr(self._repository, "list_observations"):
            raise ContractQueryError("Repository does not provide list_observations")

        rows = self._repository.list_observations()
        if not isinstance(rows, list):
            raise ContractQueryError("Repository returned invalid observation rows")
        return rows

    def fetch_by_series_key(self, series_key: str) -> list[dict[str, object]]:
        """Return all canonical rows for the requested series key."""
        rows = self._list_rows()
        return [row for row in rows if row.get("series_key") == series_key]

    def fetch_by_source_type(self, source_type: str) -> list[dict[str, object]]:
        """Return canonical rows filtered by normalized source type label."""
        normalized = source_type.strip().lower()
        rows = self._list_rows()
        return [row for row in rows if str(row.get("source_type", "")).lower() == normalized]

    def fetch_by_filters(
        self,
        *,
        source_types: set[str] | None = None,
        series_keys: set[str] | None = None,
        category_ids: set[str] | None = None,
        geography_ids: set[str] | None = None,
    ) -> list[dict[str, object]]:
        """Return canonical rows matching the provided filter matrix values."""
        rows = self._list_rows()
        normalized_source_types = (
            {value.strip().lower() for value in source_types} if source_types is not None else None
        )

        def include_row(row: dict[str, object]) -> bool:
            if normalized_source_types is not None:
                row_source_type = str(row.get("source_type", "")).lower()
                if row_source_type not in normalized_source_types:
                    return False

            if series_keys is not None and str(row.get("series_key", "")) not in series_keys:
                return False

            if category_ids is not None and str(row.get("category_id", "")) not in category_ids:
                return False

            return not (
                geography_ids is not None and str(row.get("geography_id", "")) not in geography_ids
            )

        return [row for row in rows if include_row(row)]
