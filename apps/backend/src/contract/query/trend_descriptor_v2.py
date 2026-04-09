"""Versioned trend descriptor v2 contract payload models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class OlsDiagnostics(BaseModel):
    """Supplementary OLS diagnostics payload."""

    slope: float | None = None
    intercept: float | None = None
    r_squared: float | None = None
    p_value: float | None = None


class PreprocessingMetadata(BaseModel):
    """Preprocessing metadata used by trend scoring/arbitration."""

    smoothing_method: Literal["ewma", "none"]
    smoothing_parameters: dict[str, object] = Field(default_factory=dict)
    seasonal_adjustment_method: Literal["stl", "mstl", "none"]
    seasonal_periods: list[int] = Field(default_factory=list)
    seasonal_reliability_state: Literal["reliable", "fallback_non_adjusted", "not_applicable"]
    preprocess_version: str = Field(min_length=1)


class CanonicalTrendDescriptorV2(BaseModel):
    """Canonical descriptor shape used by summary/detail/as-of payloads."""

    descriptor_version: Literal["v2"]
    descriptor_state: Literal["available", "unavailable"]
    trend_label: str | None = Field(default=None, min_length=1)
    direction: Literal["up", "down", "flat"] | None = None
    confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    selected_lookback_points: int | None = Field(default=None, ge=1)
    observed_on: str | None = Field(default=None, min_length=1)
    dominant_measure_family: Literal["theil_sen", "mixed", "none"]
    reason_code: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_unavailable_payload(self) -> CanonicalTrendDescriptorV2:
        """Unavailable descriptors must not expose directional signal fields."""
        if self.descriptor_state == "unavailable" and (
            self.direction is not None or self.confidence_score is not None
        ):
            raise ValueError(
                "unavailable canonical descriptors must not include direction/confidence"
            )
        return self


class LookbackTrendEvidenceV2(BaseModel):
    """Per-lookback evidence payload for detail and as-of responses."""

    lookback_points: Literal[1, 2, 3, 4, 5, 10, 25, 50, 100, 250, 500, 1000]
    applicability_state: Literal["applicable", "inapplicable"]
    descriptor_state: Literal["available", "unavailable"]
    trend_label: str | None = Field(default=None, min_length=1)
    direction: Literal["up", "down", "flat"] | None = None
    confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    dominant_measure_family: Literal["theil_sen", "mixed", "none"] | None = None
    theil_sen_slope: float | None = None
    theil_sen_low_slope: float | None = None
    theil_sen_high_slope: float | None = None
    kendall_tau: float | None = None
    kendall_p_value: float | None = None
    preprocessing: PreprocessingMetadata
    ols_diagnostics: OlsDiagnostics
    reason_code: str | None = Field(default=None, min_length=1)


class ObservationAsOfTrendV2Response(BaseModel):
    """As-of trend payload for one dataset and as-of observation date."""

    dataset_id: str = Field(min_length=1)
    as_of_observed_on: str = Field(min_length=1)
    canonical_trend_descriptor: CanonicalTrendDescriptorV2
    lookback_trend_evidence: list[LookbackTrendEvidenceV2]
