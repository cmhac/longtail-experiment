"""
Spike: multi-horizon trend detection with emerging/sustained labels.

Uses synthetic data to test a multi-horizon Mann-Kendall approach where:
- MK is run on multiple calendar-anchored time windows per cadence
- Short windows detect emerging trends early
- Long windows confirm sustained trends
- Stale moves (old trend that has flattened) are correctly classified as stable
- Seasonal series are detected via STL decomposition + Hyndman Fs metric
  and deseasonalized before MK analysis

No database dependency — all data is generated synthetically.

Usage:
    python research_trend_detection/spike_multi_horizon.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

import numpy as np

try:
    import pymannkendall as mk  # type: ignore[import-untyped]
except ImportError:
    print("ERROR: pymannkendall not installed. Run: pip install pymannkendall")
    sys.exit(1)

try:
    from statsmodels.tsa.seasonal import STL
except ImportError:
    print("ERROR: statsmodels not installed. Run: pip install statsmodels")
    sys.exit(1)


# ---------------------------------------------------------------------------
# 1. Types and configuration
# ---------------------------------------------------------------------------

Cadence = Literal["daily", "weekly", "monthly"]
TrendLabel = Literal[
    "strong_sustained_uptrend",
    "mild_sustained_uptrend",
    "strong_sustained_downtrend",
    "mild_sustained_downtrend",
    "emerging_uptrend",
    "emerging_downtrend",
    "stable",
]

# Calendar-anchored window definitions per cadence (in days).
# Each cadence gets a set of windows appropriate to its frequency.
# "short" windows detect emerging trends, "long" windows confirm sustained ones.
WINDOW_DEFS: dict[Cadence, list[tuple[str, int]]] = {
    "daily": [
        ("2w", 14),
        ("1m", 30),
        ("3m", 91),
        ("6m", 182),
        ("12m", 365),
    ],
    "weekly": [
        ("4w", 28),
        ("13w", 91),
        ("6m", 182),
        ("12m", 365),
    ],
    "monthly": [
        ("6m", 182),
        ("12m", 365),
    ],
}

# Minimum observations required for MK test per window.
# MK is valid down to ~5 observations, though power is low.
# We use 6 to allow 6-month windows on monthly data.
MK_MIN_OBS = 6

# MK significance threshold
MK_ALPHA = 0.05
MK_TAU_MIN = 0.15  # minimum effect size to consider meaningful

# Seasonal decomposition configuration.
# Period = expected number of observations per annual cycle for each cadence.
SEASONAL_PERIODS: dict[Cadence, int] = {
    "daily": 252,  # trading days per year
    "weekly": 52,  # weeks per year
    "monthly": 12,  # months per year
}
# Hyndman Fs metric threshold; series with Fs above this are considered seasonal.
# Fs ∈ [0, 1]; 0 = no seasonality, 1 = perfectly repeating cycle.
SEASONALITY_FS_THRESHOLD = 0.6
# Additional guardrail: require high autocorrelation at seasonal lag on
# linearly detrended data. This prevents false seasonal detection on U-shapes,
# reversals, and flat-then-breakout patterns where STL can overfit seasonality.
SEASONALITY_ACF_THRESHOLD = 0.5


@dataclass
class WindowResult:
    """Result of a MK test on a single calendar window."""

    window_name: str
    window_days: int
    obs_count: int
    mk_trend: str  # "increasing", "decreasing", "no trend"
    mk_p: float
    mk_tau: float
    pct_change: float | None  # relative % change over window
    pp_change: float | None  # absolute pp change (for percent-type series)
    significant: bool  # p < alpha AND |tau| >= tau_min
    direction: str  # "up", "down", "flat"


@dataclass
class SeasonalityInfo:
    """Summary of seasonality detection for a series."""

    period: int
    fs_score: float  # Hyndman Fs: 0 = no seasonality, 1 = perfectly seasonal
    acf_at_period: float  # detrended autocorrelation at seasonal lag
    spectral_ratio: float  # seasonal-frequency peak power / median background power
    is_seasonal: bool
    enough_data: bool  # False if < 2 full cycles available for detection


@dataclass
class MultiHorizonResult:
    """Combined result across all windows for a series."""

    series_name: str
    cadence: Cadence
    unit_type: str
    obs_count: int
    window_results: list[WindowResult]
    trend_label: TrendLabel
    classification_reason: str
    seasonality_info: SeasonalityInfo | None


# ---------------------------------------------------------------------------
# 2. Synthetic data generators
# ---------------------------------------------------------------------------


def _make_dates(
    cadence: Cadence, n_periods: int, end_date: date | None = None
) -> list[date]:
    """Generate a list of dates for a given cadence."""
    if end_date is None:
        end_date = date(2026, 3, 31)

    if cadence == "daily":
        # Skip weekends for realism
        dates = []
        d = end_date
        while len(dates) < n_periods:
            if d.weekday() < 5:  # Mon-Fri
                dates.append(d)
            d -= timedelta(days=1)
        return list(reversed(dates))
    elif cadence == "weekly":
        return [end_date - timedelta(weeks=n_periods - 1 - i) for i in range(n_periods)]
    else:  # monthly
        dates = []
        y, m = end_date.year, end_date.month
        for i in range(n_periods):
            dates.append(date(y, m, 1))
            m -= 1
            if m < 1:
                m = 12
                y -= 1
        return list(reversed(dates))


def _add_noise(values: np.ndarray, noise_pct: float = 0.5) -> np.ndarray:
    """Add random noise scaled as a percentage of the mean value."""
    rng = np.random.default_rng(42)
    mean_val = np.mean(np.abs(values))
    noise = rng.normal(0, mean_val * noise_pct / 100, len(values))
    return values + noise


@dataclass
class SyntheticSeries:
    name: str
    description: str
    expected_label: str
    cadence: Cadence
    unit_type: str
    dates: list[date]
    values: np.ndarray


def make_scenarios() -> list[SyntheticSeries]:
    """Generate synthetic series covering every classification scenario."""
    scenarios: list[SyntheticSeries] = []

    # -----------------------------------------------------------------------
    # SCENARIO 1: Sustained strong uptrend (daily, USD)
    # Steady climb over 18 months, still actively rising
    # -----------------------------------------------------------------------
    n = 390  # ~18 months of trading days
    dates = _make_dates("daily", n)
    base = 50.0
    slope = 0.05  # +$0.05/day ≈ +$13/yr on a $50 base = ~26%/yr
    values = base + np.arange(n) * slope
    values = _add_noise(values, noise_pct=1.0)
    scenarios.append(
        SyntheticSeries(
            name="SUSTAINED_STRONG_UP_DAILY",
            description="Steady daily price climbing ~26%/yr for 18 months",
            expected_label="strong_sustained_uptrend",
            cadence="daily",
            unit_type="usd",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 2: Sustained mild uptrend (weekly, USD)
    # Slow climb over 12 months
    # -----------------------------------------------------------------------
    n = 104  # 2 years of weekly
    dates = _make_dates("weekly", n)
    base = 3.50
    slope = 0.003  # +$0.003/week ≈ +$0.16/yr on $3.50 = ~4.5%/yr
    values = base + np.arange(n) * slope
    values = _add_noise(values, noise_pct=1.5)
    scenarios.append(
        SyntheticSeries(
            name="SUSTAINED_MILD_UP_WEEKLY",
            description="Slow weekly price climb ~4.5%/yr for 2 years",
            expected_label="mild_sustained_uptrend",
            cadence="weekly",
            unit_type="usd",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 3: Sustained strong downtrend (monthly, percent)
    # Interest rate dropping 3pp over 12 months (fast rate-cut cycle)
    # -----------------------------------------------------------------------
    n = 24
    dates = _make_dates("monthly", n)
    # Rate goes from 5.5% to 2.5% linearly over 24 months = ~1.5pp per 12m
    values = np.linspace(5.5, 2.5, n)
    values = _add_noise(values, noise_pct=0.3)
    scenarios.append(
        SyntheticSeries(
            name="SUSTAINED_STRONG_DOWN_MONTHLY_RATE",
            description="Interest rate dropping ~2pp over 24 months",
            expected_label="strong_sustained_downtrend",
            cadence="monthly",
            unit_type="percent",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 4: Sustained mild downtrend (monthly, percent)
    # Unemployment declining 0.8pp over 12 months
    # -----------------------------------------------------------------------
    n = 24
    dates = _make_dates("monthly", n)
    # 4.5% → 3.7% over 24 months = ~0.4pp per 12m
    values = np.linspace(4.5, 3.7, n)
    values = _add_noise(values, noise_pct=0.2)
    scenarios.append(
        SyntheticSeries(
            name="SUSTAINED_MILD_DOWN_MONTHLY_RATE",
            description="Unemployment declining ~0.8pp over 24 months",
            expected_label="mild_sustained_downtrend",
            cadence="monthly",
            unit_type="percent",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 5: Emerging uptrend (daily, USD)
    # Flat for 12 months, then sharp rise in the last 6 weeks
    # -----------------------------------------------------------------------
    n = 390
    dates = _make_dates("daily", n)
    flat_n = 360
    rise_n = n - flat_n
    flat_part = np.full(flat_n, 100.0)
    rise_part = 100.0 + np.linspace(0, 8, rise_n)  # +8% in 6 weeks
    values = np.concatenate([flat_part, rise_part])
    values = _add_noise(values, noise_pct=0.3)
    scenarios.append(
        SyntheticSeries(
            name="EMERGING_UP_DAILY",
            description="Flat 12mo then sharp +8% rise in last 6 weeks",
            expected_label="emerging_uptrend",
            cadence="daily",
            unit_type="usd",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 6: Emerging downtrend (weekly, USD)
    # Stable for 9 months, then dropping for last 8 weeks
    # -----------------------------------------------------------------------
    n = 104
    dates = _make_dates("weekly", n)
    flat_n = 96
    drop_n = n - flat_n
    flat_part = np.full(flat_n, 3.50)
    drop_part = 3.50 - np.linspace(0, 0.35, drop_n)  # -10% in 8 weeks
    values = np.concatenate([flat_part, drop_part])
    values = _add_noise(values, noise_pct=0.8)
    scenarios.append(
        SyntheticSeries(
            name="EMERGING_DOWN_WEEKLY",
            description="Stable 9mo then -10% drop in last 8 weeks",
            expected_label="emerging_downtrend",
            cadence="weekly",
            unit_type="usd",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 7: Emerging uptrend (monthly, percent)
    # Unemployment flat then jumps 0.8pp in last 6 months
    # (3 months is too few obs for any statistical test at monthly freq)
    # -----------------------------------------------------------------------
    n = 24
    dates = _make_dates("monthly", n)
    flat_n = 18
    rise_n = n - flat_n
    flat_part = np.full(flat_n, 3.8)
    rise_part = 3.8 + np.linspace(0, 0.8, rise_n)
    values = np.concatenate([flat_part, rise_part])
    values = _add_noise(values, noise_pct=0.15)
    scenarios.append(
        SyntheticSeries(
            name="EMERGING_UP_MONTHLY_RATE",
            description="Unemployment flat then +0.8pp in last 6 months",
            expected_label="emerging_uptrend",
            cadence="monthly",
            unit_type="percent",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 8: Stale move — spike then flat (daily, USD)
    # Big jump 6 months ago, completely flat since
    # -----------------------------------------------------------------------
    n = 390
    dates = _make_dates("daily", n)
    pre_spike = np.full(130, 80.0)  # first 6 months
    spike = np.linspace(80, 96, 20)  # sharp 20% jump over 1 month
    post_spike = np.full(n - 150, 96.0)  # flat for last 8+ months
    values = np.concatenate([pre_spike, spike, post_spike])
    values = _add_noise(values, noise_pct=0.4)
    scenarios.append(
        SyntheticSeries(
            name="STALE_MOVE_DAILY",
            description="20% spike 8 months ago, completely flat since",
            expected_label="stable",
            cadence="daily",
            unit_type="usd",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 9: U-shape recovery (weekly, USD)
    # Dropped then recovered — net up 12m but MK ambiguous
    # -----------------------------------------------------------------------
    n = 104
    dates = _make_dates("weekly", n)
    down = np.linspace(3.00, 2.40, 52)  # drop for first year
    up = np.linspace(2.40, 3.20, 52)  # recover + overshoot for second year
    values = np.concatenate([down, up])
    values = _add_noise(values, noise_pct=1.0)
    scenarios.append(
        SyntheticSeries(
            name="U_SHAPE_WEEKLY",
            description="Dropped 20% then recovered +33%, net +6.7% over 2yr",
            expected_label="stable",
            cadence="weekly",
            unit_type="usd",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 10: Truly flat / no trend (monthly, percent)
    # Random walk around 4.2% with no direction
    # -----------------------------------------------------------------------
    n = 24
    dates = _make_dates("monthly", n)
    rng = np.random.default_rng(99)
    values = 4.2 + rng.normal(0, 0.05, n)  # tight noise around 4.2%
    scenarios.append(
        SyntheticSeries(
            name="FLAT_MONTHLY_RATE",
            description="Random walk around 4.2%, no trend",
            expected_label="stable",
            cadence="monthly",
            unit_type="percent",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 11: Truly flat (daily, USD)
    # -----------------------------------------------------------------------
    n = 390
    dates = _make_dates("daily", n)
    rng = np.random.default_rng(77)
    values = 25.0 + rng.normal(0, 0.15, n)
    scenarios.append(
        SyntheticSeries(
            name="FLAT_DAILY_USD",
            description="Random noise around $25, no trend",
            expected_label="stable",
            cadence="daily",
            unit_type="usd",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 12: Seasonal — yearly cycle, no real trend (weekly)
    # -----------------------------------------------------------------------
    n = 104
    dates = _make_dates("weekly", n)
    t = np.arange(n)
    values = 3.0 + 0.30 * np.sin(2 * np.pi * t / 52)  # ±$0.30 annual cycle
    values = _add_noise(values, noise_pct=1.0)
    scenarios.append(
        SyntheticSeries(
            name="SEASONAL_WEEKLY",
            description="Seasonal $0.30 annual cycle around $3.00, no real trend",
            expected_label="stable",
            cadence="weekly",
            unit_type="usd",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 13: Trend reversal — was up, now turning down (weekly, USD)
    # Rising for 18 months, peaked, dropping for last 2 months
    # -----------------------------------------------------------------------
    n = 104
    dates = _make_dates("weekly", n)
    rise_n = 96
    drop_n = n - rise_n
    rise_part = 2.50 + np.linspace(0, 0.90, rise_n)  # +36% over 96 weeks
    drop_part = 3.40 - np.linspace(0, 0.25, drop_n)  # -7% over 8 weeks
    values = np.concatenate([rise_part, drop_part])
    values = _add_noise(values, noise_pct=0.8)
    scenarios.append(
        SyntheticSeries(
            name="REVERSAL_UP_TO_DOWN_WEEKLY",
            description="Rising 18mo then reversing down last 2mo",
            expected_label="emerging_downtrend",
            cadence="weekly",
            unit_type="usd",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 14: Very fast emerging trend (daily, USD)
    # Completely flat, then strong move in just the last 2 weeks
    # -----------------------------------------------------------------------
    n = 390
    dates = _make_dates("daily", n)
    flat_part = np.full(380, 60.0)
    spike_part = 60.0 + np.linspace(0, 6, 10)  # +10% in 2 weeks
    values = np.concatenate([flat_part, spike_part])
    values = _add_noise(values, noise_pct=0.2)
    scenarios.append(
        SyntheticSeries(
            name="VERY_FAST_EMERGING_UP_DAILY",
            description="Flat then +10% in last 2 weeks only",
            expected_label="emerging_uptrend",
            cadence="daily",
            unit_type="usd",
            dates=dates,
            values=values,
        )
    )

    # ===================================================================
    # SEASONAL SCENARIOS (15–20)
    # These test seasonality detection + decomposition. The classifier
    # should strip the seasonal component and detect the underlying trend.
    # ===================================================================

    # -----------------------------------------------------------------------
    # SCENARIO 15: Seasonal + strong sustained uptrend (weekly, USD)
    # Gas prices with ±$0.40 annual cycle PLUS a strong underlying rise
    # -----------------------------------------------------------------------
    n = 104  # 2 years of weekly data (exactly 2 seasonal cycles)
    dates = _make_dates("weekly", n)
    t = np.arange(n)
    base = 3.00
    seasonal = 0.40 * np.sin(2 * np.pi * t / 52)
    trend = 0.015 * t  # +$0.015/week ≈ +$0.78/yr ≈ +26% on $3.00
    values = base + trend + seasonal
    values = _add_noise(values, noise_pct=1.0)
    scenarios.append(
        SyntheticSeries(
            name="SEASONAL_STRONG_UP_WEEKLY",
            description="Weekly prices with ±$0.40 annual cycle + strong uptrend (~26%/yr)",
            expected_label="strong_sustained_uptrend",
            cadence="weekly",
            unit_type="usd",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 16: Seasonal + mild sustained uptrend (weekly, USD)
    # Prices with annual cycle PLUS mild underlying trend
    # -----------------------------------------------------------------------
    n = 104
    dates = _make_dates("weekly", n)
    t = np.arange(n)
    base = 3.00
    seasonal = 0.30 * np.sin(2 * np.pi * t / 52)
    trend = 0.003 * t  # +$0.003/week ≈ +$0.16/yr ≈ +5.2%
    values = base + trend + seasonal
    values = _add_noise(values, noise_pct=1.0)
    scenarios.append(
        SyntheticSeries(
            name="SEASONAL_MILD_UP_WEEKLY",
            description="Weekly prices with ±$0.30 annual cycle + mild uptrend (~5%/yr)",
            expected_label="mild_sustained_uptrend",
            cadence="weekly",
            unit_type="usd",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 17: Strong seasonal cycle, truly flat (monthly, percent)
    # Monthly rate with 12-month seasonal cycle, no underlying trend
    # -----------------------------------------------------------------------
    n = 36  # 3 years (3 full annual cycles for better STL fit)
    dates = _make_dates("monthly", n)
    t = np.arange(n)
    base = 4.0
    seasonal = 0.30 * np.sin(2 * np.pi * t / 12)  # ±0.30pp annual cycle
    values = base + seasonal
    values = _add_noise(values, noise_pct=0.2)
    scenarios.append(
        SyntheticSeries(
            name="SEASONAL_FLAT_MONTHLY",
            description="Monthly rate with ±0.3pp annual cycle, no trend, 3 years",
            expected_label="stable",
            cadence="monthly",
            unit_type="percent",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 18: Seasonal + emerging uptrend (weekly, USD)
    # Seasonal baseline then a recent breakout above the seasonal pattern
    # -----------------------------------------------------------------------
    n = 104
    dates = _make_dates("weekly", n)
    t = np.arange(n)
    base = 3.00
    seasonal = 0.30 * np.sin(2 * np.pi * t / 52)
    # Flat for first 90 weeks, then rising for last 14 weeks
    trend = np.zeros(n)
    breakout_start = 90
    trend[breakout_start:] = np.linspace(
        0, 0.30, n - breakout_start
    )  # +$0.30 in 14wk ≈ +10%
    values = base + trend + seasonal
    values = _add_noise(values, noise_pct=0.8)
    scenarios.append(
        SyntheticSeries(
            name="SEASONAL_EMERGING_UP_WEEKLY",
            description="Weekly seasonal baseline, flat 90wk then +$0.30 breakout in 14wk",
            expected_label="emerging_uptrend",
            cadence="weekly",
            unit_type="usd",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 19: Seasonal + strong sustained downtrend (daily, USD)
    # Daily prices with annual cycle + clear strong decline over 2.5 years
    # -----------------------------------------------------------------------
    n = 630  # ~2.5 years of trading days (need ≥504 for 2 annual cycles)
    dates = _make_dates("daily", n)
    t = np.arange(n)
    base = 80.0
    seasonal = 5.0 * np.sin(2 * np.pi * t / 252)  # ±$5 annual cycle
    trend = -0.04 * t  # −$0.04/day ≈ −$10/yr ≈ −12.5%/yr
    values = base + trend + seasonal
    values = _add_noise(values, noise_pct=0.5)
    scenarios.append(
        SyntheticSeries(
            name="SEASONAL_STRONG_DOWN_DAILY",
            description="Daily prices with ±$5 annual cycle + strong downtrend (~12.5%/yr)",
            expected_label="strong_sustained_downtrend",
            cadence="daily",
            unit_type="usd",
            dates=dates,
            values=values,
        )
    )

    # -----------------------------------------------------------------------
    # SCENARIO 20: Seasonal + mild sustained downtrend (monthly, percent)
    # Monthly rate declining slowly with annual seasonal cycle
    # -----------------------------------------------------------------------
    n = 36  # 3 years of monthly data (3 full annual cycles)
    dates = _make_dates("monthly", n)
    t = np.arange(n)
    base = 5.0
    seasonal = 0.20 * np.sin(2 * np.pi * t / 12)  # ±0.20pp annual cycle
    trend = -0.04 * t  # −0.04pp/month ≈ −0.48pp/yr → mild over 12 months
    values = base + trend + seasonal
    values = _add_noise(values, noise_pct=0.15)
    scenarios.append(
        SyntheticSeries(
            name="SEASONAL_MILD_DOWN_MONTHLY",
            description="Monthly rate with ±0.2pp annual cycle + mild downtrend (~0.5pp/yr)",
            expected_label="mild_sustained_downtrend",
            cadence="monthly",
            unit_type="percent",
            dates=dates,
            values=values,
        )
    )

    return scenarios


# ---------------------------------------------------------------------------
# 3. Seasonality detection and decomposition
# ---------------------------------------------------------------------------


def _linear_detrend(values: np.ndarray) -> np.ndarray:
    """Remove linear trend from a series."""
    n = len(values)
    if n <= 1:
        return values - float(np.mean(values))

    x = np.arange(n, dtype=float)
    x_c = x - np.mean(x)
    denom = float(np.dot(x_c, x_c))
    if denom == 0:
        return values - float(np.mean(values))

    slope = float(np.dot(x_c, values - np.mean(values)) / denom)
    intercept = float(np.mean(values) - slope * float(np.mean(x)))
    return values - (slope * x + intercept)


def _acf_at_lag(values: np.ndarray, lag: int) -> float:
    """Compute autocorrelation at a specific lag on already-detrended data."""
    n = len(values)
    if lag <= 0 or n <= lag:
        return 0.0

    centered = values - float(np.mean(values))
    var = float(np.var(centered))
    if var == 0:
        return 0.0

    a = centered[: n - lag]
    b = centered[lag:]
    cov = float(np.mean(a * b))
    return cov / var


def _seasonal_spectral_ratio(values: np.ndarray, period: int) -> float:
    """Estimate strength of a seasonal frequency peak in detrended data."""
    if len(values) < 4:
        return 0.0

    detrended = _linear_detrend(values)
    fft_vals = np.fft.rfft(detrended)
    if len(fft_vals) <= 2:
        return 0.0

    power = np.abs(fft_vals[1:]) ** 2
    freqs = np.fft.rfftfreq(len(detrended), d=1.0)[1:]
    if len(freqs) == 0:
        return 0.0

    target_freq = 1.0 / period
    idx = int(np.argmin(np.abs(freqs - target_freq)))
    lo = max(0, idx - 1)
    hi = min(len(power), idx + 2)
    peak = float(np.max(power[lo:hi]))

    mask = np.ones(len(power), dtype=bool)
    mask[lo:hi] = False
    for h in (2, 3):
        hf = h * target_freq
        h_idx = int(np.argmin(np.abs(freqs - hf)))
        hlo = max(0, h_idx - 1)
        hhi = min(len(power), h_idx + 2)
        mask[hlo:hhi] = False

    bg = power[mask]
    bg_median = float(np.median(bg)) if len(bg) > 0 else 0.0
    if bg_median <= 0:
        return 0.0
    return peak / bg_median


def detect_seasonality(values: np.ndarray, period: int) -> SeasonalityInfo:
    """Detect if a series has significant seasonality using STL + Hyndman Fs.

    Hyndman's strength-of-seasonality metric:
        Fs = 1 - Var(R) / Var(S + R)
    where S = seasonal component, R = residual from STL decomposition.
    Fs ∈ [0, 1]; higher values indicate stronger seasonality.

    Requires at least 2 full seasonal cycles for reliable detection.
    """
    if len(values) < 2 * period:
        return SeasonalityInfo(
            period=period,
            fs_score=0.0,
            acf_at_period=0.0,
            spectral_ratio=0.0,
            is_seasonal=False,
            enough_data=False,
        )

    detrended = _linear_detrend(values)
    acf_p = _acf_at_lag(detrended, period)
    spectral_ratio = _seasonal_spectral_ratio(values, period)

    try:
        stl = STL(values, period=period, robust=True)
        result = stl.fit()
    except Exception:
        return SeasonalityInfo(
            period=period,
            fs_score=0.0,
            acf_at_period=acf_p,
            spectral_ratio=spectral_ratio,
            is_seasonal=False,
            enough_data=True,
        )

    seasonal = result.seasonal
    residual = result.resid

    var_sr = float(np.var(seasonal + residual))
    if var_sr == 0:
        return SeasonalityInfo(
            period=period,
            fs_score=0.0,
            acf_at_period=acf_p,
            spectral_ratio=spectral_ratio,
            is_seasonal=False,
            enough_data=True,
        )

    fs = max(0.0, 1.0 - float(np.var(residual)) / var_sr)
    is_seasonal = fs > SEASONALITY_FS_THRESHOLD and acf_p > SEASONALITY_ACF_THRESHOLD

    return SeasonalityInfo(
        period=period,
        fs_score=fs,
        acf_at_period=acf_p,
        spectral_ratio=spectral_ratio,
        is_seasonal=is_seasonal,
        enough_data=True,
    )


def deseasonalize(values: np.ndarray, period: int) -> np.ndarray:
    """Remove seasonal component using STL decomposition.

    Returns trend + residual (everything except the repeating seasonal part).
    """
    stl = STL(values, period=period, robust=True)
    result = stl.fit()
    return result.trend + result.resid


# ---------------------------------------------------------------------------
# 4. Multi-horizon MK analysis
# ---------------------------------------------------------------------------


def find_nearest_obs(
    dates: list[date], values: np.ndarray, target_date: date
) -> tuple[date, float] | None:
    """Find the observation with the date closest to target_date."""
    if not dates:
        return None
    best_idx = 0
    best_dist = abs((dates[0] - target_date).days)
    for i, d in enumerate(dates):
        dist = abs((d - target_date).days)
        if dist < best_dist:
            best_dist = dist
            best_idx = i
    # Don't match if the nearest observation is more than 15 days away
    if best_dist > 15:
        return None
    return dates[best_idx], float(values[best_idx])


def run_mk_on_window(
    dates: list[date],
    values: np.ndarray,
    window_name: str,
    window_days: int,
    unit_type: str,
) -> WindowResult | None:
    """Run MK test on observations within a calendar window."""
    latest_date = dates[-1]
    cutoff = latest_date - timedelta(days=window_days)

    # Filter to window
    mask = [d >= cutoff for d in dates]
    window_dates = [d for d, m in zip(dates, mask) if m]
    window_values = values[mask]

    if len(window_values) < MK_MIN_OBS:
        return None

    # Run MK test
    try:
        mk_result = mk.hamed_rao_modification_test(window_values, alpha=MK_ALPHA)
    except Exception:
        try:
            mk_result = mk.original_test(window_values, alpha=MK_ALPHA)
        except Exception:
            return None

    # Calendar-anchored percent change: latest vs value at start of window
    pct_change = None
    pp_change = None
    start_val = float(window_values[0])
    end_val = float(window_values[-1])
    if start_val != 0:
        pct_change = (end_val - start_val) / start_val * 100
    pp_change = end_val - start_val

    significant = mk_result.p < MK_ALPHA and abs(mk_result.Tau) >= MK_TAU_MIN

    if mk_result.trend == "increasing":
        direction = "up"
    elif mk_result.trend == "decreasing":
        direction = "down"
    else:
        direction = "flat"

    return WindowResult(
        window_name=window_name,
        window_days=window_days,
        obs_count=len(window_values),
        mk_trend=mk_result.trend,
        mk_p=mk_result.p,
        mk_tau=mk_result.Tau,
        pct_change=pct_change,
        pp_change=pp_change,
        significant=significant,
        direction=direction,
    )


def _check_u_shape(
    dates: list[date],
    values: np.ndarray,
    longest_sig: WindowResult,
) -> bool:
    """Check if the longest window contains a U-shape (direction reversal).

    Splits the window observations in half and compares OLS slopes.
    If the halves have opposite slope signs, it's a U-shape.
    """
    latest_date = dates[-1]
    cutoff = latest_date - timedelta(days=longest_sig.window_days)
    mask = [d >= cutoff for d in dates]
    window_values = values[np.array(mask)]

    if len(window_values) < 10:  # need enough for meaningful halves
        return False

    mid = len(window_values) // 2
    first_half = window_values[:mid]
    second_half = window_values[mid:]

    def _ols_slope(v: np.ndarray) -> float:
        x = np.arange(len(v), dtype=float)
        x_c = x - np.mean(x)
        denom = np.dot(x_c, x_c)
        if denom == 0:
            return 0.0
        return float(np.dot(x_c, v - np.mean(v)) / denom)

    slope1 = _ols_slope(first_half)
    slope2 = _ols_slope(second_half)

    # U-shape: slopes have opposite signs and both are meaningful
    # (at least 1% of the mean value per observation)
    mean_val = np.mean(np.abs(window_values))
    min_slope = mean_val * 0.001 if mean_val > 0 else 0
    if abs(slope1) > min_slope and abs(slope2) > min_slope:
        if (slope1 > 0 and slope2 < 0) or (slope1 < 0 and slope2 > 0):
            return True
    return False


def classify_multi_horizon(
    window_results: list[WindowResult],
    unit_type: str,
    dates: list[date] | None = None,
    values: np.ndarray | None = None,
    apply_near_zero_filter: bool = True,
) -> tuple[TrendLabel, str]:
    """Classify trend using multi-horizon MK results.

    Strategy:
    1. Find all significant windows and their directions.
    2. Handle conflicting directions: shortest significant window represents
       the CURRENT direction — this is an emerging trend (reversal).
       Require minimum |τ| ≥ 0.4 on the short window to filter noise.
    3. U-shape detection: if the longest window's halves contradict, classify stable.
    4. If all agree, decide emerging vs sustained by checking whether significance
       is concentrated in short windows or spans the full range.
    5. Stale moves: only detected when short windows EXIST, are non-significant,
       AND their tau direction disagrees with the long window.
    """
    if not window_results:
        return "stable", "no_windows_available"

    sig_results = [w for w in window_results if w.significant]

    if not sig_results:
        return "stable", "no_significant_windows"

    # Sort everything by window size
    sorted_all = sorted(window_results, key=lambda w: w.window_days)
    sig_by_size = sorted(sig_results, key=lambda w: w.window_days)

    shortest_sig = sig_by_size[0]
    longest_sig = sig_by_size[-1]

    # --- Conflicting directions among significant windows ---
    directions = {w.direction for w in sig_results}
    if len(directions) > 1:
        # Before calling this a reversal, check if the longest window's net change
        # is near zero — that signals seasonal oscillation, not a real reversal.
        longest_all = sorted_all[-1]
        if longest_all.pct_change is not None and abs(longest_all.pct_change) < 2.0:
            return "stable", (
                f"seasonal_oscillation(conflicting_dirs,"
                f"net_pct={longest_all.pct_change:+.2f}%@{longest_all.window_name})"
            )

        # Short and long windows disagree — only call it an emerging reversal
        # if the short window has a strong signal (|τ| ≥ 0.4), otherwise it's noise.
        if abs(shortest_sig.mk_tau) >= 0.4:
            trend_dir = shortest_sig.direction
            label: TrendLabel = (
                "emerging_uptrend" if trend_dir == "up" else "emerging_downtrend"
            )
            mag_pct = shortest_sig.pct_change or 0
            return label, (
                f"reversal_emerging(current={shortest_sig.window_name}:{trend_dir},"
                f"historical={longest_sig.window_name}:{longest_sig.direction},"
                f"pct={mag_pct:+.2f}%)"
            )
        else:
            return "stable", (
                f"conflicting_but_weak_recent("
                f"short={shortest_sig.window_name}:τ={shortest_sig.mk_tau:+.3f},"
                f"long={longest_sig.window_name}:τ={longest_sig.mk_tau:+.3f})"
            )

    # All significant windows agree on direction
    trend_dir = sig_results[0].direction

    # --- Seasonal / oscillation filter ---
    # Keep this for non-deseasonalized series to suppress pure cycles.
    # After decomposition, net changes can be naturally compressed, so this
    # gate is skipped to avoid hiding true emerging moves.
    longest_all = sorted_all[-1]  # longest window regardless of significance
    if apply_near_zero_filter:
        if longest_all.pct_change is not None and abs(longest_all.pct_change) < 2.0:
            # Net change < 2% over longest window — likely oscillation
            return "stable", (
                f"near_zero_net_change(window={longest_all.window_name},"
                f"net_pct={longest_all.pct_change:+.2f}%)"
            )

    # --- U-shape detection ---
    # Check the FULL data for a direction reversal (not just the MK window),
    # since U-shapes often span the entire observation period.
    if dates is not None and values is not None and len(values) >= 10:
        mid = len(values) // 2
        first_half = values[:mid]
        second_half = values[mid:]

        def _ols_slope_quick(v: np.ndarray) -> float:
            x = np.arange(len(v), dtype=float)
            x_c = x - np.mean(x)
            denom = np.dot(x_c, x_c)
            if denom == 0:
                return 0.0
            return float(np.dot(x_c, v - np.mean(v)) / denom)

        s1 = _ols_slope_quick(first_half)
        s2 = _ols_slope_quick(second_half)
        mean_val = np.mean(np.abs(values))
        min_slope = mean_val * 0.001 if mean_val > 0 else 0
        if abs(s1) > min_slope and abs(s2) > min_slope:
            if (s1 > 0 and s2 < 0) or (s1 < 0 and s2 > 0):
                return "stable", (
                    f"u_shape_detected(slope1={s1:+.4f},slope2={s2:+.4f},"
                    f"halves_contradict)"
                )

    # --- Stale move detection ---
    # Only applies when short windows EXIST, are non-significant, AND their
    # tau direction disagrees with or is ambiguous vs the long window.
    # If short windows' tau agrees (same sign), it's a slow/mild sustained trend.
    short_threshold_days = 100
    short_windows = [w for w in sorted_all if w.window_days <= short_threshold_days]
    if short_windows:
        short_all_flat = all(not w.significant for w in short_windows)
        long_windows_sig = [
            w for w in sig_results if w.window_days > short_threshold_days
        ]
        if short_all_flat and long_windows_sig:
            # Check if the short windows' tau at least agrees in direction
            long_dir_up = long_windows_sig[0].direction == "up"
            short_tau_agrees = any((w.mk_tau > 0) == long_dir_up for w in short_windows)
            if not short_tau_agrees:
                return "stable", (
                    f"stale_move(long_sig={long_windows_sig[0].window_name},"
                    f"short_disagree=[{','.join(w.window_name for w in short_windows)}])"
                )
            # Short tau agrees but not significant — slow sustained trend, continue

    # --- Emerging vs sustained ---
    long_threshold_days = 180

    # Key insight: if the 12m window is NOT significant but shorter windows are,
    # the trend hasn't persisted for a full year — it's emerging, even if the
    # longest significant window is >= 6 months.
    longest_all_window = sorted_all[-1]  # the actual longest window we tested
    twelve_month_not_sig = (
        longest_all_window.window_days >= 300  # we have a ~12m window
        and not longest_all_window.significant
    )

    # Case 1: 12m exists but is not significant → trend is recent/emerging
    if twelve_month_not_sig:
        label = "emerging_uptrend" if trend_dir == "up" else "emerging_downtrend"
        return label, (
            f"emerging_12m_not_sig(longest_sig={longest_sig.window_name},"
            f"12m_tau={longest_all_window.mk_tau:+.3f},"
            f"pct={longest_sig.pct_change or 0:+.2f}%)"
        )

    # Case 2: Longest significant window is short (< 6 months)
    if longest_sig.window_days < long_threshold_days:
        label = "emerging_uptrend" if trend_dir == "up" else "emerging_downtrend"
        return label, (
            f"emerging_short_horizon(longest_sig={longest_sig.window_name},"
            f"τ={longest_sig.mk_tau:+.3f},"
            f"pct={longest_sig.pct_change or 0:+.2f}%)"
        )

    # Case 3: Tau concentration — if short τ >> long τ, trend is recent/emerging
    tau_ratio = abs(shortest_sig.mk_tau) / max(abs(longest_sig.mk_tau), 0.01)
    concentrated_at_recent = (tau_ratio > 1.8 and abs(shortest_sig.mk_tau) > 0.4) or (
        abs(longest_sig.mk_tau) < 0.25 and abs(shortest_sig.mk_tau) > 0.4
    )

    if concentrated_at_recent and shortest_sig.window_days < longest_sig.window_days:
        label = "emerging_uptrend" if trend_dir == "up" else "emerging_downtrend"
        return label, (
            f"emerging(short_tau={shortest_sig.mk_tau:+.3f}@{shortest_sig.window_name},"
            f"long_tau={longest_sig.mk_tau:+.3f}@{longest_sig.window_name},"
            f"ratio={tau_ratio:.2f},"
            f"pct={shortest_sig.pct_change or 0:+.2f}%)"
        )

    # --- Sustained trend — classify by magnitude ---
    magnitude_pct = longest_sig.pct_change
    magnitude_pp = longest_sig.pp_change

    if unit_type == "percent":
        mag = abs(magnitude_pp or 0)
        if mag > 1.5:
            strength = "strong"
        elif mag > 0.3:
            strength = "mild"
        else:
            return "stable", f"sustained_but_tiny_pp({magnitude_pp:+.4f}pp)"
        reason = (
            f"sustained_{strength}(pp={magnitude_pp:+.4f}pp,"
            f"shortest={shortest_sig.window_name},"
            f"longest={longest_sig.window_name})"
        )
    else:
        mag = abs(magnitude_pct or 0)
        if mag > 10:
            strength = "strong"
        elif mag > 3:
            strength = "mild"
        else:
            return "stable", f"sustained_but_tiny_pct({magnitude_pct:+.2f}%)"
        reason = (
            f"sustained_{strength}(pct={magnitude_pct:+.2f}%,"
            f"shortest={shortest_sig.window_name},"
            f"longest={longest_sig.window_name})"
        )

    if trend_dir == "up":
        label = f"{strength}_sustained_uptrend"  # type: ignore[assignment]
    else:
        label = f"{strength}_sustained_downtrend"  # type: ignore[assignment]

    return label, reason


def analyze_series(series: SyntheticSeries) -> MultiHorizonResult:
    """Run multi-horizon analysis on a single synthetic series."""
    # --- Seasonality detection and decomposition ---
    period = SEASONAL_PERIODS[series.cadence]
    seasonality = detect_seasonality(series.values, period)

    # Baseline classification on raw values.
    # This remains important for seasonal emerging breakouts where full-series
    # decomposition can compress net change and understate short, meaningful moves.
    raw_window_results: list[WindowResult] = []
    for window_name, window_days in WINDOW_DEFS[series.cadence]:
        raw_result = run_mk_on_window(
            series.dates,
            series.values,
            window_name,
            window_days,
            series.unit_type,
        )
        if raw_result is not None:
            raw_window_results.append(raw_result)

    raw_label, raw_reason = classify_multi_horizon(
        raw_window_results,
        series.unit_type,
        series.dates,
        series.values,
        apply_near_zero_filter=True,
    )

    if seasonality.is_seasonal:
        analysis_values = deseasonalize(series.values, period)
    else:
        analysis_values = series.values

    windows = WINDOW_DEFS[series.cadence]
    window_results: list[WindowResult] = []

    for window_name, window_days in windows:
        result = run_mk_on_window(
            series.dates,
            analysis_values,
            window_name,
            window_days,
            series.unit_type,
        )
        if result is not None:
            window_results.append(result)

    label, reason = classify_multi_horizon(
        window_results,
        series.unit_type,
        series.dates,
        analysis_values,
        apply_near_zero_filter=not seasonality.is_seasonal,
    )

    # If seasonal decomposition flattens magnitude enough to return stable but
    # raw windows indicate a clear emerging move, trust the raw emerging signal.
    # This preserves rapid breakout detection in strongly seasonal series.
    if seasonality.is_seasonal:
        if (
            label == "stable"
            and reason.startswith("sustained_but_tiny_")
            and raw_label in {"emerging_uptrend", "emerging_downtrend"}
        ):
            label = raw_label
            reason = (
                f"seasonal_blend(use_raw_emerging;raw={raw_reason};deseason={reason})"
            )

    return MultiHorizonResult(
        series_name=series.name,
        cadence=series.cadence,
        unit_type=series.unit_type,
        obs_count=len(series.values),
        window_results=window_results,
        trend_label=label,
        classification_reason=reason,
        seasonality_info=seasonality,
    )


# ---------------------------------------------------------------------------
# 4. Output and main
# ---------------------------------------------------------------------------


def print_window_detail(wr: WindowResult) -> None:
    """Print a single window result."""
    sig_marker = "SIG" if wr.significant else "n/s"
    pct_str = f"{wr.pct_change:+.2f}%" if wr.pct_change is not None else "N/A"
    pp_str = f"{wr.pp_change:+.4f}pp" if wr.pp_change is not None else "N/A"
    print(
        f"      {wr.window_name:<5} "
        f"{wr.obs_count:>4} obs  "
        f"[{sig_marker}] "
        f"p={wr.mk_p:<8.4f} "
        f"τ={wr.mk_tau:+.3f}  "
        f"Δ%={pct_str:<10} "
        f"Δpp={pp_str}"
    )


def main() -> None:
    print("=" * 100)
    print("MULTI-HORIZON TREND DETECTION SPIKE — Synthetic Data")
    print("=" * 100)
    print()

    scenarios = make_scenarios()
    results: list[MultiHorizonResult] = []

    for series in scenarios:
        result = analyze_series(series)
        results.append(result)

    # --- Per-scenario detail ---
    pass_count = 0
    fail_count = 0

    for series, result in zip(scenarios, results):
        match = result.trend_label == series.expected_label
        status = "✓ PASS" if match else "✗ FAIL"
        if match:
            pass_count += 1
        else:
            fail_count += 1

        print(f"  [{status}] {series.name} ({series.cadence}, {series.unit_type})")
        print(f"    Description: {series.description}")
        print(f"    Expected:    {series.expected_label}")
        print(f"    Got:         {result.trend_label}")
        print(f"    Reason:      {result.classification_reason}")
        if result.seasonality_info:
            si = result.seasonality_info
            sea_tag = "SEASONAL" if si.is_seasonal else "non-seasonal"
            data_tag = "" if si.enough_data else " (insufficient data for detection)"
            print(
                f"    Seasonality: {sea_tag} "
                f"(Fs={si.fs_score:.3f}, ACF={si.acf_at_period:.3f}, "
                f"Spectral={si.spectral_ratio:.2f}, period={si.period}){data_tag}"
            )
        print(f"    Windows ({len(result.window_results)}):")
        for wr in result.window_results:
            print_window_detail(wr)
        print()

    # --- Summary ---
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"  Total scenarios:  {len(results)}")
    print(f"  Passed:           {pass_count}")
    print(f"  Failed:           {fail_count}")
    print()

    if fail_count > 0:
        print("  FAILED SCENARIOS:")
        for series, result in zip(scenarios, results):
            if result.trend_label != series.expected_label:
                print(
                    f"    {series.name}: expected={series.expected_label}, "
                    f"got={result.trend_label} — {result.classification_reason}"
                )
    print()

    # --- Label distribution ---
    from collections import Counter

    label_counts = Counter(r.trend_label for r in results)
    print("  LABEL DISTRIBUTION:")
    for label in sorted(label_counts.keys()):
        print(f"    {label:<30}: {label_counts[label]}")


if __name__ == "__main__":
    main()
