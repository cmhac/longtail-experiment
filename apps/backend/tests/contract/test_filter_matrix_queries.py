"""FR-010 tests for backend full filter-matrix contract behavior."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.query.canonical_query import CanonicalObservationQueryService

_FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "filter_matrix_scenarios.json"


class _FilterMatrixRepo:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = rows

    def list_observations(self) -> list[dict[str, object]]:
        return list(self._rows)


def test_filter_matrix_scenarios_match_expected_series() -> None:
    """All fixture scenarios should resolve to the expected series keys."""
    payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    service = CanonicalObservationQueryService(repository=_FilterMatrixRepo(payload["rows"]))

    for scenario in payload["scenarios"]:
        rows = service.fetch_by_filters(
            source_types=set(scenario.get("source_types", [])) or None,
            series_keys=set(scenario.get("series_keys", [])) or None,
            category_ids=set(scenario.get("category_ids", [])) or None,
            geography_ids=set(scenario.get("geography_ids", [])) or None,
        )
        assert {str(row["series_key"]) for row in rows} == set(scenario["expected_series"])
