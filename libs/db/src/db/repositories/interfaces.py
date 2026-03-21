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
