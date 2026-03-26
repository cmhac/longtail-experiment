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
                "date": "2026-01-01",
                "reported_at": datetime(2026, 2, 2, tzinfo=UTC),
                "value": Decimal("3.1"),
            }
        )


def test_payload_mapper_maps_dataset_metadata_aliases() -> None:
    """Mapper should support metadata aliases used by source adapters."""
    observation = normalize_source_payload(
        {
            "source_name": "FRED",
            "source_type": "EXTERNAL",
            "series_key": "INT.US.FEDFUNDS",
            "metric_name": "Effective Federal Funds Rate",
            "title": "Effective Federal Funds Rate",
            "description": "Federal funds effective interest rate.",
            "geographic_scope": "United States",
            "tags": ["interest rates", "monetary policy"],
            "date": "2026-01-01",
            "reported_at": datetime(2026, 2, 2, tzinfo=UTC),
            "value": Decimal("4.1"),
        }
    )

    assert observation.dataset_title == "Effective Federal Funds Rate"
    assert observation.dataset_description == "Federal funds effective interest rate."
    assert observation.dataset_geographic_scope == "United States"
    assert observation.topic_tags == ["interest rates", "monetary policy"]


def test_payload_mapper_normalizes_explicit_unit_type_and_attributes() -> None:
    """Mapper should normalize explicit unit_type and persist it in attributes."""
    observation = normalize_source_payload(
        {
            "source_name": "FRED",
            "source_type": "EXTERNAL",
            "series_key": "INT.US.FEDFUNDS",
            "metric_name": "Effective Federal Funds Rate",
            "date": "2026-01-01",
            "reported_at": datetime(2026, 2, 2, tzinfo=UTC),
            "value": Decimal("4.1"),
            "unit_type": "PERCENT",
            "attributes": {"revision": 0},
        }
    )

    assert observation.unit_type == "percent"
    assert observation.attributes["unit_type"] == "percent"
    assert observation.attributes["revision"] == "0"


def test_payload_mapper_infers_unit_type_from_unit_label() -> None:
    """Mapper should infer percent/usd/number unit_type from unit labels."""
    percent_observation = normalize_source_payload(
        {
            "source_name": "FRED",
            "source_type": "EXTERNAL",
            "series_key": "INT.US.FEDFUNDS",
            "metric_name": "Effective Federal Funds Rate",
            "date": "2026-01-01",
            "reported_at": datetime(2026, 2, 2, tzinfo=UTC),
            "value": Decimal("4.1"),
            "unit": "Percent",
        }
    )
    usd_observation = normalize_source_payload(
        {
            "source_name": "EIA",
            "source_type": "EXTERNAL",
            "series_key": "ENERGY.US.GASREGW",
            "metric_name": "US Regular Gas Price",
            "date": "2026-01-01",
            "reported_at": datetime(2026, 2, 2, tzinfo=UTC),
            "value": Decimal("3.21"),
            "unit": "Dollars per Gallon",
        }
    )
    number_observation = normalize_source_payload(
        {
            "source_name": "BLS",
            "source_type": "EXTERNAL",
            "series_key": "CPI.US.ALL",
            "metric_name": "Consumer Price Index",
            "date": "2026-01-01",
            "reported_at": datetime(2026, 2, 2, tzinfo=UTC),
            "value": Decimal("302.5"),
            "unit": "Index",
        }
    )

    assert percent_observation.unit_type == "percent"
    assert usd_observation.unit_type == "usd"
    assert number_observation.unit_type == "number"
