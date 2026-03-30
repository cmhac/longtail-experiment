"""US1 schema validation tests for canonical observations."""

from __future__ import annotations

import sys
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.schemas.canonical_observation import CanonicalObservation


def test_canonical_observation_accepts_valid_payload() -> None:
    """A complete canonical payload should validate successfully."""
    payload = CanonicalObservation(
        source_key="bls_cpi",
        source_name="BLS",
        source_title="Bureau of Labor Statistics",
        source_description="US labor market and price statistics.",
        source_type="external",
        series_key="CPI.US.ALL",
        metric_name="Consumer Price Index",
        dataset_title="US Consumer Price Index",
        dataset_description="Headline CPI for urban consumers.",
        dataset_geographic_scope="United States",
        topic_tags=["inflation", "prices"],
        observed_on=date(2026, 1, 1),
        reported_at=datetime(2026, 2, 1, tzinfo=UTC),
        value=Decimal("302.5000"),
        unit="index",
        unit_type="number",
        attributes={"seasonally_adjusted": "true"},
    )

    assert payload.series_key == "CPI.US.ALL"
    assert payload.dataset_geographic_scope == "United States"
    assert payload.topic_tags == ["inflation", "prices"]
    assert payload.unit_type == "number"


def test_canonical_observation_requires_mandatory_fields() -> None:
    """Missing required fields should raise a Pydantic validation error."""
    with pytest.raises(ValidationError):
        CanonicalObservation.model_validate(
            {
                "source_name": "BLS",
                "source_key": "bls_cpi",
                "source_title": "Bureau of Labor Statistics",
                "source_description": "US labor market and price statistics.",
                "source_type": "external",
                "metric_name": "Consumer Price Index",
                "observed_on": date(2026, 1, 1),
                "reported_at": datetime(2026, 2, 1, tzinfo=UTC),
                "value": Decimal("302.5000"),
            }
        )


def test_canonical_observation_rejects_invalid_unit_type() -> None:
    """Schema should reject unit_type values outside usd/percent/number."""
    with pytest.raises(ValidationError):
        CanonicalObservation.model_validate(
            {
                "source_name": "BLS",
                "source_key": "bls_cpi",
                "source_title": "Bureau of Labor Statistics",
                "source_description": "US labor market and price statistics.",
                "source_type": "external",
                "series_key": "CPI.US.ALL",
                "metric_name": "Consumer Price Index",
                "observed_on": date(2026, 1, 1),
                "reported_at": datetime(2026, 2, 1, tzinfo=UTC),
                "value": Decimal("302.5000"),
                "unit_type": "ratio",
            }
        )
