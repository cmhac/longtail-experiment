"""Preprocessing helpers for trend-analysis v2 scoring."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import PreprocessingMetadata

import pandas as pd

from .models import PreprocessingMetadata
from .version import LIBRARY_VERSION


def apply_ewma(
    values: list[float], *, halflife: float = 3.0
) -> tuple[list[float], PreprocessingMetadata]:
    """Apply default EWMA smoothing and return v2 preprocessing metadata."""

    series = pd.Series(values, dtype="float64")
    smoothed = series.ewm(halflife=halflife, adjust=False, ignore_na=True, min_periods=1).mean()
    metadata = PreprocessingMetadata(
        smoothing_method="ewma",
        smoothing_parameters={
            "halflife": halflife,
            "adjust": False,
            "ignore_na": True,
            "min_periods": 1,
        },
        seasonal_adjustment_method="none",
        seasonal_periods=(),
        seasonal_reliability_state="not_applicable",
        preprocess_version=LIBRARY_VERSION,
    )
    return [float(value) for value in smoothed.tolist()], metadata
