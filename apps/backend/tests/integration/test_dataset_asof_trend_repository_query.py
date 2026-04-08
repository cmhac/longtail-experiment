"""Integration coverage for repository as-of trend query methods."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.query.trend_descriptor_v2 import ObservationAsOfTrendV2Response
from src.query.dataset_asof_trend_query import execute_dataset_asof_trend
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

        if "FROM trend_lookback_evaluations tle" in sql and "target_observation" in sql:
            if dataset_id != "UNRATE":
                return _FakeResult([])
            return _FakeResult(
                [
                    {
                        "lookback_points": 25,
                        "applicability_state": "applicable",
                        "descriptor_state": "available",
                        "trend_label": "",
                        "direction": "up",
                        "confidence_score": 0.73,
                        "dominant_measure_family": "theil_sen",
                        "theil_sen_slope": 0.2,
                        "theil_sen_low_slope": 0.1,
                        "theil_sen_high_slope": 0.3,
                        "kendall_tau": 0.4,
                        "kendall_p_value": 0.01,
                        "preprocessing": {},
                        "ols_diagnostics": {
                            "slope": 0.2,
                            "intercept": 1.0,
                            "r_squared": 0.5,
                            "p_value": 0.02,
                        },
                        "reason_code": "",
                    },
                    {
                        "lookback_points": 1000,
                        "applicability_state": "inapplicable",
                        "descriptor_state": "unavailable",
                        "trend_label": None,
                        "direction": None,
                        "confidence_score": None,
                        "dominant_measure_family": None,
                        "theil_sen_slope": None,
                        "theil_sen_low_slope": None,
                        "theil_sen_high_slope": None,
                        "kendall_tau": None,
                        "kendall_p_value": None,
                        "preprocessing": {},
                        "ols_diagnostics": {
                            "slope": None,
                            "intercept": None,
                            "r_squared": None,
                            "p_value": None,
                        },
                        "reason_code": "cadence_lookback_not_supported",
                    },
                ]
            )

        if "FROM trend_canonical_descriptors tcd" in sql and "CAST(:observed_on AS date)" in sql:
            if dataset_id != "UNRATE":
                return _FakeResult([])
            return _FakeResult(
                [
                    {
                        "descriptor_version": "v2",
                        "descriptor_state": "available",
                        "trend_label": "",
                        "direction": "up",
                        "confidence_score": 0.73,
                        "selected_lookback_points": 25,
                        "observed_on": date(2026, 3, 1),
                        "dominant_measure_family": "theil_sen",
                        "reason_code": "",
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


def test_repository_asof_methods_project_v2_payloads() -> None:
    repository = PersistedDatasetDiscoveryRepository(engine=_FakeEngine())  # type: ignore[arg-type]

    descriptor = repository.get_canonical_descriptor_for_observed_on(
        dataset_id="UNRATE",
        observed_on=date(2026, 3, 1),
    )
    evidence = repository.list_lookback_evidence_for_observed_on(
        dataset_id="UNRATE",
        observed_on=date(2026, 3, 1),
    )

    assert descriptor == {
        "descriptor_version": "v2",
        "descriptor_state": "available",
        "trend_label": None,
        "direction": "up",
        "confidence_score": 0.73,
        "selected_lookback_points": 25,
        "observed_on": "2026-03-01",
        "dominant_measure_family": "theil_sen",
        "reason_code": None,
    }
    assert evidence[0]["preprocessing"] == {
        "smoothing_method": "none",
        "smoothing_parameters": {},
        "seasonal_adjustment_method": "none",
        "seasonal_periods": [],
        "seasonal_reliability_state": "not_applicable",
        "preprocess_version": "v2",
    }
    assert evidence[0]["trend_label"] is None
    assert evidence[0]["reason_code"] is None


def test_repository_asof_methods_return_empty_for_missing_dataset() -> None:
    repository = PersistedDatasetDiscoveryRepository(engine=_FakeEngine())  # type: ignore[arg-type]

    descriptor = repository.get_canonical_descriptor_for_observed_on(
        dataset_id="MISSING",
        observed_on=date(2026, 3, 1),
    )
    evidence = repository.list_lookback_evidence_for_observed_on(
        dataset_id="MISSING",
        observed_on=date(2026, 3, 1),
    )

    assert descriptor is None
    assert evidence == []


def test_execute_dataset_asof_trend_returns_validated_response() -> None:
    class _Service:
        def get_dataset_as_of_trend(
            self, *, dataset_id: str, as_of_observed_on: str
        ) -> dict[str, Any]:
            return {
                "dataset_id": dataset_id,
                "as_of_observed_on": as_of_observed_on,
                "canonical_trend_descriptor": {
                    "descriptor_version": "v2",
                    "descriptor_state": "available",
                    "trend_label": "mild_sustained_uptrend",
                    "direction": "up",
                    "confidence_score": 0.73,
                    "selected_lookback_points": 25,
                    "observed_on": as_of_observed_on,
                    "dominant_measure_family": "theil_sen",
                    "reason_code": None,
                },
                "lookback_trend_evidence": [
                    {
                        "lookback_points": 25,
                        "applicability_state": "applicable",
                        "descriptor_state": "available",
                        "trend_label": "mild_sustained_uptrend",
                        "direction": "up",
                        "confidence_score": 0.73,
                        "dominant_measure_family": "theil_sen",
                        "theil_sen_slope": 0.2,
                        "theil_sen_low_slope": 0.1,
                        "theil_sen_high_slope": 0.3,
                        "kendall_tau": 0.4,
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
                            "slope": 0.2,
                            "intercept": 1.0,
                            "r_squared": 0.5,
                            "p_value": 0.02,
                        },
                        "reason_code": None,
                    }
                ],
            }

    response = execute_dataset_asof_trend(
        _Service(),  # type: ignore[arg-type]
        dataset_id="UNRATE",
        as_of_observed_on="2026-03-01",
    )

    assert isinstance(response, ObservationAsOfTrendV2Response)
    assert response.dataset_id == "UNRATE"
