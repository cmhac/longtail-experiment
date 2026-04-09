"""US2 contract tests for lookback evidence payloads in dataset detail."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_detail_query import execute_dataset_detail
from src.query.dataset_discovery_service import DatasetDiscoveryService
from tests.fixtures.dataset_discovery_factory import build_discovery_rows
from tests.fixtures.dataset_discovery_repository import InMemoryDatasetDiscoveryRepository

_EXPECTED_EVIDENCE_COUNT = 2
_LOOKBACK_SHORT = 10
_CONFIDENCE_SCORE = 0.72
_LOOKBACK_LONG = 500


def _lookback_row(
    *, lookback_points: int, applicability_state: str, reason_code: str | None
) -> dict:
    return {
        "lookback_points": lookback_points,
        "applicability_state": applicability_state,
        "descriptor_state": "available" if applicability_state == "applicable" else "unavailable",
        "trend_label": (
            "mild_sustained_downtrend" if applicability_state == "applicable" else None
        ),
        "direction": "down" if applicability_state == "applicable" else None,
        "confidence_score": 0.72 if applicability_state == "applicable" else None,
        "dominant_measure_family": "theil_sen" if applicability_state == "applicable" else "none",
        "theil_sen_slope": -0.12 if applicability_state == "applicable" else None,
        "theil_sen_low_slope": -0.15 if applicability_state == "applicable" else None,
        "theil_sen_high_slope": -0.10 if applicability_state == "applicable" else None,
        "kendall_tau": -0.63 if applicability_state == "applicable" else None,
        "kendall_p_value": 0.02 if applicability_state == "applicable" else None,
        "preprocessing": {
            "smoothing_method": "ewma",
            "smoothing_parameters": {"halflife": 3},
            "seasonal_adjustment_method": "none",
            "seasonal_periods": [],
            "seasonal_reliability_state": "not_applicable",
            "preprocess_version": "v2",
        },
        "ols_diagnostics": {
            "slope": -0.11 if applicability_state == "applicable" else None,
            "intercept": 4.2 if applicability_state == "applicable" else None,
            "r_squared": 0.61 if applicability_state == "applicable" else None,
            "p_value": 0.03 if applicability_state == "applicable" else None,
        },
        "reason_code": reason_code,
    }


def test_dataset_detail_includes_lookback_evidence_rows_with_applicability_states() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
        lookback_snapshots_by_dataset={
            "UNRATE": [
                _lookback_row(
                    lookback_points=10,
                    applicability_state="applicable",
                    reason_code=None,
                ),
                _lookback_row(
                    lookback_points=500,
                    applicability_state="inapplicable",
                    reason_code="insufficient_history",
                ),
            ]
        },
    )
    service = DatasetDiscoveryService(repository)

    response = execute_dataset_detail(
        service,
        dataset_id="UNRATE",
        from_date=None,
        to_date=None,
    ).model_dump()

    assert len(response["lookback_trend_evidence"]) == _EXPECTED_EVIDENCE_COUNT
    assert response["lookback_trend_evidence"][0]["lookback_points"] == _LOOKBACK_SHORT
    assert response["lookback_trend_evidence"][0]["confidence_score"] == _CONFIDENCE_SCORE
    assert response["lookback_trend_evidence"][0]["dominant_measure_family"] == "theil_sen"
    assert response["lookback_trend_evidence"][1]["lookback_points"] == _LOOKBACK_LONG
    assert response["lookback_trend_evidence"][1]["reason_code"] == "insufficient_history"


def test_dataset_detail_returns_empty_lookback_evidence_list_when_absent() -> None:
    datasets, observations = build_discovery_rows()
    repository = InMemoryDatasetDiscoveryRepository(
        datasets=datasets,
        observations=observations,
    )
    service = DatasetDiscoveryService(repository)

    response = execute_dataset_detail(
        service,
        dataset_id="UNRATE",
        from_date=None,
        to_date=None,
    ).model_dump()

    assert response["lookback_trend_evidence"] == []
