"""US2 tests for revision lineage integrity behavior."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.schemas.revision_record import RevisionRecord
from src.contract.services.revision_lineage_service import RevisionLineageService


def test_revision_record_rejects_identical_observation_ids() -> None:
    """Revision links must connect two distinct observation versions."""
    with pytest.raises(ValidationError):
        RevisionRecord(
            superseded_observation_id="obs-001",
            current_observation_id="obs-001",
            revision_reason="source-correction",
            series_key="CPI.US.ALL",
            reference_period_start=date(2026, 1, 1),
            reference_period_end=date(2026, 1, 31),
        )


def test_revision_lineage_service_requires_matching_series() -> None:
    """Lineage service must reject links where series keys do not match."""
    service = RevisionLineageService()

    with pytest.raises(ValueError):
        service.link_revision(
            superseded={
                "observation_id": "obs-old",
                "series_key": "CPI.US.ALL",
                "reference_period_start": date(2026, 1, 1),
                "reference_period_end": date(2026, 1, 31),
            },
            current={
                "observation_id": "obs-new",
                "series_key": "TEMP.US.NYC",
                "reference_period_start": date(2026, 1, 1),
                "reference_period_end": date(2026, 1, 31),
            },
            revision_reason="restatement",
        )


def test_revision_lineage_service_rejects_mismatched_periods() -> None:
    """Lineage links must preserve identical reference period semantics."""
    service = RevisionLineageService()

    with pytest.raises(ValueError):
        service.link_revision(
            superseded={
                "observation_id": "obs-old",
                "series_key": "CPI.US.ALL",
                "reference_period_start": date(2026, 1, 1),
                "reference_period_end": date(2026, 1, 31),
            },
            current={
                "observation_id": "obs-new",
                "series_key": "CPI.US.ALL",
                "reference_period_start": date(2026, 1, 1),
                "reference_period_end": date(2026, 2, 1),
            },
            revision_reason="restatement",
        )


def test_revision_lineage_service_builds_revision_record() -> None:
    """Valid lineage inputs should produce a normalized revision record."""
    service = RevisionLineageService()

    record = service.link_revision(
        superseded={
            "observation_id": "obs-old",
            "series_key": "CPI.US.ALL",
            "reference_period_start": "2026-01-01",
            "reference_period_end": "2026-01-31",
        },
        current={
            "observation_id": "obs-new",
            "series_key": "CPI.US.ALL",
            "reference_period_start": "2026-01-01",
            "reference_period_end": "2026-01-31",
        },
        revision_reason="restatement",
    )

    assert record.superseded_observation_id == "obs-old"
    assert record.current_observation_id == "obs-new"
