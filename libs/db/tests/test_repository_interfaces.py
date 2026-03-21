"""Tests for repository and session foundational contracts."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from db.repositories.interfaces import ObservationRepository, ProvenanceRepository


class _ObservationRepoImpl:
    def upsert_value(self, series_key: str, observed_on: date, value: Decimal) -> None:
        return None


class _ProvenanceRepoImpl:
    def add_release(
        self, observation_id: str, release_id: str, source_url: str
    ) -> None:
        return None


def test_observation_repository_shape() -> None:
    repo = _ObservationRepoImpl()
    assert isinstance(repo, ObservationRepository)


def test_provenance_repository_shape() -> None:
    repo = _ProvenanceRepoImpl()
    assert isinstance(repo, ProvenanceRepository)
