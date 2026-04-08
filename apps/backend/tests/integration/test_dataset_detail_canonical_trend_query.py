"""US2 integration tests for canonical trend descriptor query behavior."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.dataset_discovery_persisted_repository import PersistedDatasetDiscoveryRepository


class _FakeResult:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def mappings(self) -> _FakeResult:
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows


class _FakeConnection:
    def execute(
        self,
        statement: object,
        parameters: dict[str, object] | None = None,
    ) -> _FakeResult:
        params = parameters or {}
        dataset_id = str(params.get("dataset_id", ""))
        sql = str(statement)
        if "FROM trend_lookback_evaluations tle" in sql:
            if dataset_id != "UNRATE":
                return _FakeResult([])
            return _FakeResult(
                [
                    {
                        "lookback_points": 10,
                        "applicability_state": "applicable",
                        "descriptor_state": "available",
                        "trend_label": "mild_sustained_downtrend",
                        "direction": "down",
                        "confidence_score": 0.64,
                        "dominant_measure_family": "theil_sen",
                        "theil_sen_slope": -0.1,
                        "theil_sen_low_slope": -0.2,
                        "theil_sen_high_slope": -0.05,
                        "kendall_tau": -0.41,
                        "kendall_p_value": 0.01,
                        "preprocessing": {
                            "smoothing_method": "none",
                            "smoothing_parameters": {},
                            "seasonal_adjustment_method": "none",
                            "seasonal_periods": [],
                            "seasonal_reliability_state": "not_applicable",
                            "preprocess_version": "v2",
                        },
                        "ols_diagnostics": {
                            "slope": -0.09,
                            "intercept": 4.7,
                            "r_squared": 0.55,
                            "p_value": 0.02,
                        },
                        "reason_code": None,
                    },
                    {
                        "lookback_points": 500,
                        "applicability_state": "inapplicable",
                        "descriptor_state": "unavailable",
                        "trend_label": None,
                        "direction": None,
                        "confidence_score": None,
                        "dominant_measure_family": "none",
                        "theil_sen_slope": None,
                        "theil_sen_low_slope": None,
                        "theil_sen_high_slope": None,
                        "kendall_tau": None,
                        "kendall_p_value": None,
                        "preprocessing": {
                            "smoothing_method": "none",
                            "smoothing_parameters": {},
                            "seasonal_adjustment_method": "none",
                            "seasonal_periods": [],
                            "seasonal_reliability_state": "not_applicable",
                            "preprocess_version": "v2",
                        },
                        "ols_diagnostics": {
                            "slope": None,
                            "intercept": None,
                            "r_squared": None,
                            "p_value": None,
                        },
                        "reason_code": "insufficient_history",
                    },
                ]
            )
        if "FROM trend_canonical_descriptors tcd" in sql:
            if dataset_id != "UNRATE":
                return _FakeResult([])
            return _FakeResult(
                [
                    {
                        "descriptor_version": "v2",
                        "descriptor_state": "available",
                        "trend_label": "mild_sustained_downtrend",
                        "direction": "down",
                        "confidence_score": 0.64,
                        "selected_lookback_points": 25,
                        "observed_on": "2026-03-01",
                        "dominant_measure_family": "theil_sen",
                        "reason_code": None,
                    }
                ]
            )
        raise AssertionError(f"Unexpected SQL executed: {sql}")

    def __enter__(self) -> _FakeConnection:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        del exc_type, exc, tb


class _FakeEngine:
    def connect(self) -> _FakeConnection:
        return _FakeConnection()


def test_repository_reads_latest_canonical_descriptor_projection() -> None:
    """Repository should return canonical descriptor for the requested dataset."""
    repository = PersistedDatasetDiscoveryRepository(engine=_FakeEngine())  # type: ignore[arg-type]

    payload = repository.get_latest_dataset_canonical_trend_descriptor(dataset_id="UNRATE")

    assert payload == {
        "descriptor_version": "v2",
        "descriptor_state": "available",
        "trend_label": "mild_sustained_downtrend",
        "direction": "down",
        "confidence_score": 0.64,
        "selected_lookback_points": 25,
        "observed_on": "2026-03-01",
        "dominant_measure_family": "theil_sen",
        "reason_code": None,
    }


def test_repository_returns_none_when_no_canonical_descriptor_exists() -> None:
    """Repository should return None when no canonical descriptor row exists."""

    class _NoRowsConnection(_FakeConnection):
        def execute(
            self, statement: object, parameters: dict[str, object] | None = None
        ) -> _FakeResult:
            del parameters
            sql = str(statement)
            if "FROM trend_canonical_descriptors tcd" in sql:
                return _FakeResult([])
            raise AssertionError(f"Unexpected SQL executed: {sql}")

    class _NoRowsEngine:
        def connect(self) -> _NoRowsConnection:
            return _NoRowsConnection()

    repository = PersistedDatasetDiscoveryRepository(engine=_NoRowsEngine())  # type: ignore[arg-type]

    payload = repository.get_latest_dataset_canonical_trend_descriptor(dataset_id="UNRATE")

    assert payload is None


def test_repository_reads_lookback_evidence_projection_for_latest_observation() -> None:
    """Repository should return lookback evidence for latest evaluated observation."""
    repository = PersistedDatasetDiscoveryRepository(engine=_FakeEngine())  # type: ignore[arg-type]

    payload = repository.list_dataset_lookback_evidence(dataset_id="UNRATE")

    assert payload == [
        {
            "lookback_points": 10,
            "applicability_state": "applicable",
            "descriptor_state": "available",
            "trend_label": "mild_sustained_downtrend",
            "direction": "down",
            "confidence_score": 0.64,
            "dominant_measure_family": "theil_sen",
            "theil_sen_slope": -0.1,
            "theil_sen_low_slope": -0.2,
            "theil_sen_high_slope": -0.05,
            "kendall_tau": -0.41,
            "kendall_p_value": 0.01,
            "preprocessing": {
                "smoothing_method": "none",
                "smoothing_parameters": {},
                "seasonal_adjustment_method": "none",
                "seasonal_periods": [],
                "seasonal_reliability_state": "not_applicable",
                "preprocess_version": "v2",
            },
            "ols_diagnostics": {
                "slope": -0.09,
                "intercept": 4.7,
                "r_squared": 0.55,
                "p_value": 0.02,
            },
            "reason_code": None,
        },
        {
            "lookback_points": 500,
            "applicability_state": "inapplicable",
            "descriptor_state": "unavailable",
            "trend_label": None,
            "direction": None,
            "confidence_score": None,
            "dominant_measure_family": "none",
            "theil_sen_slope": None,
            "theil_sen_low_slope": None,
            "theil_sen_high_slope": None,
            "kendall_tau": None,
            "kendall_p_value": None,
            "preprocessing": {
                "smoothing_method": "none",
                "smoothing_parameters": {},
                "seasonal_adjustment_method": "none",
                "seasonal_periods": [],
                "seasonal_reliability_state": "not_applicable",
                "preprocess_version": "v2",
            },
            "ols_diagnostics": {
                "slope": None,
                "intercept": None,
                "r_squared": None,
                "p_value": None,
            },
            "reason_code": "insufficient_history",
        },
    ]
