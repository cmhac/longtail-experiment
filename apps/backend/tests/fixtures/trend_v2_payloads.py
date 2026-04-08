"""Shared backend payload fixtures for spec 050 trend descriptor v2 contracts."""

from __future__ import annotations


def canonical_available_v2() -> dict[str, object]:
    return {
        "descriptor_version": "v2",
        "descriptor_state": "available",
        "trend_label": "moderate_uptrend",
        "direction": "up",
        "confidence_score": 0.74,
        "selected_lookback_points": 25,
        "observed_on": "2026-03-01",
        "dominant_measure_family": "theil_sen",
        "reason_code": None,
    }


def canonical_unavailable_v2() -> dict[str, object]:
    return {
        "descriptor_version": "v2",
        "descriptor_state": "unavailable",
        "trend_label": None,
        "direction": None,
        "confidence_score": None,
        "selected_lookback_points": None,
        "observed_on": "2026-03-01",
        "dominant_measure_family": "none",
        "reason_code": "cadence_irregular_rejected",
    }


def lookback_evidence_v2() -> list[dict[str, object]]:
    return [
        {
            "lookback_points": 25,
            "applicability_state": "applicable",
            "descriptor_state": "available",
            "trend_label": "moderate_uptrend",
            "direction": "up",
            "confidence_score": 0.74,
            "dominant_measure_family": "theil_sen",
            "theil_sen_slope": 1.22,
            "theil_sen_low_slope": 0.8,
            "theil_sen_high_slope": 1.58,
            "kendall_tau": 0.61,
            "kendall_p_value": 0.003,
            "preprocessing": {
                "smoothing_method": "ewma",
                "smoothing_parameters": {"halflife": 3},
                "seasonal_adjustment_method": "none",
                "seasonal_periods": [],
                "seasonal_reliability_state": "not_applicable",
                "preprocess_version": "v2",
            },
            "ols_diagnostics": {
                "slope": 1.15,
                "intercept": 98.2,
                "r_squared": 0.67,
                "p_value": 0.01,
            },
            "reason_code": None,
        },
        {
            "lookback_points": 100,
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


def lookback_evidence_v2_with_observed_on(*, observed_on: str) -> list[dict[str, object]]:
    rows = lookback_evidence_v2()
    for row in rows:
        row["observed_on"] = observed_on
    return rows
