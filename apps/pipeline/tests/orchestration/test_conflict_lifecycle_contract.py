"""US3 conflict lifecycle contract tests."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.jobs.conflict_persistence_service import (
    ConflictInput,
    ConflictPersistenceService,
)


class _ConflictRepository:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def add_conflict(self, payload: dict[str, object]) -> None:
        self.rows.append(payload)


def test_conflict_persistence_starts_with_open_state() -> None:
    """Persisted conflicts should default to open state with generated identifier."""
    repo = _ConflictRepository()
    service = ConflictPersistenceService(repository=repo)

    row = service.persist_conflict(
        ConflictInput(
            run_id="run-1",
            source_key="bls",
            series_key="CPI.US.ALL",
            reference_period_key="2026-01",
            existing_observation_ref="obs-old",
            incoming_record_ref="rec-new",
            conflict_type="value_mismatch",
        )
    )

    assert row["conflict_state"] == "open"
    assert str(row["conflict_id"]).startswith("conf-")
    assert len(repo.rows) == 1
