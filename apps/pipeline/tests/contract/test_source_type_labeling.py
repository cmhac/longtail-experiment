"""FR-009 tests for source-type labeling in pipeline canonical normalization."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.normalizers.source_payload_mapper import normalize_source_payload


def test_source_type_is_normalized_to_lowercase_labels() -> None:
    """Mapper should normalize source type labels to canonical lowercase values."""
    observation = normalize_source_payload(
        {
            "source_name": "BLS",
            "source_type": "EXTERNAL",
            "series_key": "CPI.US.ALL",
            "metric_name": "Consumer Price Index",
            "frequency": "monthly",
            "date": "2026-01-01",
            "reported_at": datetime(2026, 2, 1, tzinfo=UTC),
            "value": Decimal("302.5"),
        }
    )

    assert observation.source_type == "external"


def test_source_type_rejects_non_contract_values() -> None:
    """Schema should reject values outside internal/external source labels."""
    with pytest.raises(ValidationError):
        normalize_source_payload(
            {
                "source_name": "Derived",
                "source_type": "partner",
                "series_key": "TEMP.US.NYC",
                "metric_name": "Average Temperature",
                "frequency": "monthly",
                "date": "2026-01-01",
                "reported_at": datetime(2026, 2, 2, tzinfo=UTC),
                "value": Decimal("3.1"),
            }
        )
