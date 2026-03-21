"""FR-009 tests for backend source-type query filtering."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.query.canonical_query import CanonicalObservationQueryService


class _SourceTypeRepo:
    def list_observations(self) -> list[dict[str, object]]:
        return [
            {"series_key": "CPI.US.ALL", "source_type": "external"},
            {"series_key": "PIPELINE.QUALITY", "source_type": "internal"},
            {"series_key": "TEMP.US.NYC", "source_type": "external"},
        ]


def test_fetch_by_source_type_returns_only_matching_rows() -> None:
    """Source-type filter should return rows that match the requested label."""
    service = CanonicalObservationQueryService(repository=_SourceTypeRepo())

    rows = service.fetch_by_source_type("external")

    assert {str(row["series_key"]) for row in rows} == {"CPI.US.ALL", "TEMP.US.NYC"}


def test_fetch_by_source_type_normalizes_filter_input() -> None:
    """Filter API should accept mixed-case source-type query values."""
    service = CanonicalObservationQueryService(repository=_SourceTypeRepo())

    rows = service.fetch_by_source_type(" INTERNAL ")

    assert len(rows) == 1
    assert rows[0]["series_key"] == "PIPELINE.QUALITY"
