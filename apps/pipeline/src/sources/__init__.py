"""Maintained pipeline source adapter package."""

from .eia_retail_fuel_prices_source import (
    EIA_RETAIL_FUEL_PRICES_SOURCE_KEY,
    build_eia_retail_fuel_prices_source_workflow,
)
from .fred_fedfunds_source import (
    FRED_FEDFUNDS_SOURCE_KEY,
    build_fred_fedfunds_source_workflow,
)
from .nyfed_college_labor_market_source import (
    NYFED_COLLEGE_LABOR_MARKET_SOURCE_KEY,
    build_nyfed_college_labor_market_source_workflow,
)

__all__ = [
    "EIA_RETAIL_FUEL_PRICES_SOURCE_KEY",
    "FRED_FEDFUNDS_SOURCE_KEY",
    "NYFED_COLLEGE_LABOR_MARKET_SOURCE_KEY",
    "build_eia_retail_fuel_prices_source_workflow",
    "build_fred_fedfunds_source_workflow",
    "build_nyfed_college_labor_market_source_workflow",
]
