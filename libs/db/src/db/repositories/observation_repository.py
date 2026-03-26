"""Shared observation repository implementation for canonical ingest/query."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any


class InMemoryObservationRepository:
    """In-memory repository used for contract tests and local service wiring."""

    def __init__(self) -> None:
        self._rows: dict[tuple[str, date], dict[str, Any]] = {}

    def upsert_value(self, series_key: str, observed_on: date, value: Decimal) -> None:
        """Insert or replace one observation value."""
        self._rows[(series_key, observed_on)] = {
            "series_key": series_key,
            "observed_on": observed_on,
            "value": value,
        }

    def upsert_observation(self, observation: Any) -> None:
        """Insert or replace a fully normalized observation."""
        self._rows[(observation.series_key, observation.observed_on)] = {
            "series_key": observation.series_key,
            "metric_name": observation.metric_name,
            "source_type": observation.source_type,
            "observed_on": observation.observed_on,
            "reported_at": observation.reported_at,
            "value": observation.value,
            "attributes": observation.attributes,
        }

    def list_observations(self) -> list[dict[str, Any]]:
        """Return stored observations sorted by series/date for deterministic reads."""
        return [
            self._rows[key]
            for key in sorted(self._rows.keys(), key=lambda item: (item[0], item[1]))
        ]
