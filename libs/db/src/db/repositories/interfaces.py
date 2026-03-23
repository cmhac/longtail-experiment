"""Repository interface contracts for shared DB interactions."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Protocol, runtime_checkable


@runtime_checkable
class ObservationRepository(Protocol):
    """Contract for persisting and reading canonical observations."""

    def upsert_value(self, series_key: str, observed_on: date, value: Decimal) -> None:
        """Insert or replace an observation value."""


@runtime_checkable
class ProvenanceRepository(Protocol):
    """Contract for storing immutable provenance records."""

    def add_release(
        self, observation_id: str, release_id: str, source_url: str
    ) -> None:
        """Attach release metadata to an observation."""


@runtime_checkable
class HierarchyRepository(Protocol):
    """Contract for hierarchy descendant lookups used by backend filters."""

    def get_descendant_ids(self, node_id: str) -> list[str]:
        """Return descendant node ids for category or geography filters."""


@runtime_checkable
class DatasetDiscoveryReadRepository(Protocol):
    """Contract for search, catalog, recent, and detail read workflows."""

    def search_datasets(
        self,
        *,
        query_text: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict[str, object]], int]:
        """Return paginated dataset search items and total item count."""

    def list_recent_datasets(self, *, limit: int) -> list[dict[str, object]]:
        """Return recent dataset summaries ordered by recency descending."""

    def list_catalog_datasets(
        self,
        *,
        query_text: str | None,
        source_id: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict[str, object]], int]:
        """Return paginated catalog items with optional filters and total count."""

    def get_dataset_detail(self, *, dataset_id: str) -> dict[str, object] | None:
        """Return metadata for one dataset by canonical identifier."""

    def list_dataset_observations(
        self,
        *,
        dataset_id: str,
        from_date: date | None,
        to_date: date | None,
    ) -> list[dict[str, object]]:
        """Return one dataset's observations in ascending observed date order."""
