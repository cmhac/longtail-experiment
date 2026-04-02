"""
Spike: trend detection on real observation data.

Reads all series from the local database, runs Mann-Kendall trend test
and supporting metrics, prints a summary table. Does NOT write anything
back to the database.

Usage:
    uv run --project apps/backend python research_trend_detection/spike_trend_detection.py
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from decimal import Decimal

import numpy as np
from sqlalchemy import create_engine, text

# ---------------------------------------------------------------------------
# 1. Connect to local database
# ---------------------------------------------------------------------------

DATABASE_URL = "postgresql+psycopg://longtail:longtail@127.0.0.1:55432/longtail_local"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ---------------------------------------------------------------------------
# 2. Load series metadata
# ---------------------------------------------------------------------------

SERIES_QUERY = text("""
    SELECT
        ds.series_key,
        ds.title,
        ds.geographic_scope,
        sp.source_name
    FROM data_series ds
    JOIN source_profiles sp ON sp.id = ds.source_profile_id
    ORDER BY ds.series_key
""")

OBS_QUERY = text("""
    SELECT o.observed_on, o.value, o.attributes
    FROM observations o
    JOIN data_series ds ON ds.id = o.series_id
    WHERE ds.series_key = :series_key
    ORDER BY o.observed_on ASC
""")


def load_series_list() -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(SERIES_QUERY).mappings().all()
    return [dict(r) for r in rows]


def load_observations(series_key: str) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(OBS_QUERY, {"series_key": series_key}).mappings().all()
    return [
        {
            "observed_on": r["observed_on"],
            "value": float(r["value"]),
            "attributes": r["attributes"] or {},
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# 3. Trend detection functions
# ---------------------------------------------------------------------------

try:
    import pymannkendall as mk  # type: ignore[import-untyped]
except ImportError:
    print("ERROR: pymannkendall not installed. Run: pip install pymannkendall")
    sys.exit(1)


def infer_unit_type(
    observations: list[dict], attributes_fallback: str | None = None
) -> str:
    """Infer unit_type from observation attributes."""
    for obs in reversed(observations):
        ut = obs.get("attributes", {}).get("unit_type")
        if ut in ("usd", "percent", "number"):
            return ut
    if attributes_fallback:
        return attributes_fallback
    return "number"


def pct_change_window(values: np.ndarray, window: int) -> float | None:
    """Relative percent change from window observations ago to latest."""
    if len(values) < window + 1:
        return None
    latest = values[-1]
    prior = values[-(window + 1)]
    if prior == 0:
        return None
    return float((latest - prior) / prior * 100)


def pp_change_window(values: np.ndarray, window: int) -> float | None:
    """Absolute percentage-point difference from window observations ago to latest.

    Use for series whose values are already in percent (rates, unemployment, etc.).
    """
    if len(values) < window + 1:
        return None
    latest = values[-1]
    prior = values[-(window + 1)]
    return float(latest - prior)


def infer_cadence(dates: list) -> str:
    """Infer whether series is weekly or monthly from median observation gap."""
    if len(dates) < 3:
        return "unknown"
    gaps = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    median_gap = sorted(gaps)[len(gaps) // 2]
    if median_gap <= 10:
        return "weekly"
    if median_gap <= 45:
        return "monthly"
    return "quarterly"


def smoothed_direction_count(values: np.ndarray, cadence: str) -> tuple[str, int]:
    """Count consecutive same-direction moves using smoothed values.

    For weekly data, smooth with a 4-week SMA first.
    For monthly data, use raw values (each point is already a monthly aggregate).
    Returns (direction, count) of consecutive smoothed moves at the tail.
    """
    if cadence == "weekly" and len(values) >= 8:
        # 4-week SMA to suppress weekly noise
        kernel = np.ones(4) / 4
        smoothed = np.convolve(values, kernel, mode="valid")
    else:
        smoothed = values

    diffs = np.diff(smoothed)
    if len(diffs) == 0:
        return "flat", 0

    last_sign: str | None = None
    count = 0
    for d in reversed(diffs):
        sign = "up" if d > 0 else ("down" if d < 0 else "flat")
        if last_sign is None:
            last_sign = sign
            count = 1
        elif sign == last_sign:
            count += 1
        else:
            break
    return last_sign or "flat", count


def compute_recent_half_slope(values: np.ndarray) -> float:
    """OLS slope on the second half of the window, normalized as % per obs."""
    n = len(values)
    half = n // 2
    recent = values[half:]
    if len(recent) < 4:
        return 0.0
    x = np.arange(len(recent), dtype=float)
    mean_val = np.mean(recent)
    if mean_val == 0:
        return 0.0
    # Simple OLS slope
    x_centered = x - np.mean(x)
    slope = np.dot(x_centered, recent - np.mean(recent)) / np.dot(
        x_centered, x_centered
    )
    return float(slope / mean_val * 100)


def run_trend_analysis(
    series_key: str,
    observations: list[dict],
    lookback_months: int = 24,
) -> dict | None:
    """
    Run the full trend detection pipeline on recent observations.

    Uses the most recent `lookback_months` of data to focus on current trends
    rather than detecting trends across the full 30+ year history.
    """
    if len(observations) < 10:
        return None

    # Filter to recent window
    all_dates = [obs["observed_on"] for obs in observations]
    all_values = np.array([obs["value"] for obs in observations])
    latest_date = all_dates[-1]

    cutoff = latest_date - timedelta(days=lookback_months * 30)
    mask = np.array([d >= cutoff for d in all_dates])
    recent_values = all_values[mask]
    recent_dates = [d for d, m in zip(all_dates, mask) if m]

    if len(recent_values) < 10:
        return None

    # --- Mann-Kendall (Hamed-Rao for autocorrelation correction) ---
    try:
        mk_result = mk.hamed_rao_modification_test(recent_values, alpha=0.05)
    except Exception:
        # Fallback to original test if Hamed-Rao fails (e.g., too few obs)
        try:
            mk_result = mk.original_test(recent_values, alpha=0.05)
        except Exception:
            return None

    # --- Percent change metrics (observation-count windows, not calendar) ---
    pct_12obs = (
        pct_change_window(recent_values, 12) if len(recent_values) > 12 else None
    )
    pct_6obs = pct_change_window(recent_values, 6) if len(recent_values) > 6 else None
    pct_3obs = pct_change_window(recent_values, 3) if len(recent_values) > 3 else None
    pp_12obs = pp_change_window(recent_values, 12) if len(recent_values) > 12 else None

    # --- Recent-half slope (detects U-shape vs true monotonic) ---
    recent_half_slope_pct = compute_recent_half_slope(recent_values)

    # --- Infer cadence and compute smoothed momentum ---
    cadence = infer_cadence(recent_dates)
    consec_dir, consec_count = smoothed_direction_count(recent_values, cadence)

    # --- Unit-type-aware label classification ---
    unit_type = infer_unit_type(observations)

    label, gate_notes = classify_trend(
        mk_trend=mk_result.trend,
        mk_p=mk_result.p,
        mk_tau=mk_result.Tau,
        pct_12obs=pct_12obs,
        pp_12obs=pp_12obs,
        recent_half_slope_pct=recent_half_slope_pct,
        unit_type=unit_type,
        consec_dir=consec_dir,
        consec_count=consec_count,
    )

    return {
        "series_key": series_key,
        "obs_count_total": len(all_values),
        "obs_count_window": len(recent_values),
        "window_start": str(recent_dates[0]),
        "window_end": str(recent_dates[-1]),
        "unit_type": unit_type,
        # Mann-Kendall
        "mk_trend": mk_result.trend,
        "mk_p": round(mk_result.p, 6),
        "mk_tau": round(mk_result.Tau, 4),
        "mk_slope": round(float(mk_result.slope), 6),
        # Percent change (observation-count windows)
        "pct_3obs": round(pct_3obs, 2) if pct_3obs is not None else None,
        "pct_6obs": round(pct_6obs, 2) if pct_6obs is not None else None,
        "pct_12obs": round(pct_12obs, 2) if pct_12obs is not None else None,
        "pp_12obs": round(pp_12obs, 4) if pp_12obs is not None else None,
        # Recent half slope
        "recent_half_slope_pct": round(recent_half_slope_pct, 4),
        # Momentum
        "consec_dir": consec_dir,
        "consec_count": consec_count,
        "cadence": cadence,
        # Final label
        "trend_label": label,
        "gate_notes": gate_notes,
    }


def classify_trend(
    *,
    mk_trend: str,
    mk_p: float,
    mk_tau: float,
    pct_12obs: float | None,
    pp_12obs: float | None,
    recent_half_slope_pct: float,
    unit_type: str,
    consec_dir: str,
    consec_count: int,
) -> tuple[str, str]:
    """Classify trend into a user-facing label using the layered gate approach.

    Returns (label, gate_notes) where gate_notes explains why this label was chosen.
    """

    # Gate 1: MK must be significant with meaningful effect size
    if mk_p >= 0.05:
        return "stable", "gate1:mk_not_significant(p={:.4f})".format(mk_p)
    if abs(mk_tau) < 0.1:
        return "stable", "gate1:mk_tau_too_weak(tau={:.4f})".format(mk_tau)

    # Gate 2: Momentum — require evidence of recent directional persistence.
    # For strong MK results (|tau| >= 0.5) with agreeing recent-half slope,
    # relax the consecutive requirement since the overall signal is very strong.
    has_momentum = consec_count >= 3 and consec_dir in ("up", "down")
    strong_mk = abs(mk_tau) >= 0.5
    slope_agrees_with_mk = (mk_trend == "increasing" and recent_half_slope_pct > 0) or (
        mk_trend == "decreasing" and recent_half_slope_pct < 0
    )
    if not has_momentum and not (strong_mk and slope_agrees_with_mk):
        return (
            "stable",
            f"gate2:no_momentum(consec={consec_dir}x{consec_count},tau={mk_tau:.3f},slope2nd={recent_half_slope_pct:+.3f}%)",
        )

    # Gate 3: Direction consistency — MK direction must agree with recent evidence.
    # Use recent-half slope as the direction arbiter (more robust than raw consecutive
    # direction for volatile weekly data). If MK and slope agree, that's the trend.
    # If they contradict, no clear trend.
    mk_direction_up = mk_trend == "increasing"
    if mk_direction_up and recent_half_slope_pct < 0:
        return (
            "stable",
            f"gate3:recent_slope_contradicts(mk=up,slope={recent_half_slope_pct:.4f}%)",
        )
    if not mk_direction_up and recent_half_slope_pct > 0:
        return (
            "stable",
            f"gate3:recent_slope_contradicts(mk=down,slope={recent_half_slope_pct:.4f}%)",
        )

    # Gate 4: Classify magnitude using 12-obs % change
    if pct_12obs is None:
        # Not enough data for 12-obs comparison — but we passed all other gates,
        # so use MK direction for a mild label.
        label = "mild_uptrend" if mk_direction_up else "mild_downtrend"
        return label, "gate4:no_12obs_data,mild_from_mk"

    # Direction consistency between pct_12obs and MK trend
    if mk_direction_up and pct_12obs < 0:
        return (
            "stable",
            f"gate4:pct12obs_contradicts_mk(mk=up,pct12obs={pct_12obs:.2f}%)",
        )
    if not mk_direction_up and pct_12obs > 0:
        return (
            "stable",
            f"gate4:pct12obs_contradicts_mk(mk=down,pct12obs={pct_12obs:.2f}%)",
        )

    if unit_type == "percent":
        # For rate series: use actual percentage-point change, not relative %
        pp = pp_12obs if pp_12obs is not None else pct_12obs
        if pp is None:
            return "stable", "gate4:no_12obs_data_for_percent"
        # Direction consistency: pp must agree with MK
        if mk_direction_up and pp < 0:
            return "stable", f"gate4:pp12m_contradicts_mk(mk=up,pp12m={pp:+.2f}pp)"
        if not mk_direction_up and pp > 0:
            return "stable", f"gate4:pp12m_contradicts_mk(mk=down,pp12m={pp:+.2f}pp)"
        abs_pp = abs(pp)
        if abs_pp > 1.5:
            label = "strong_uptrend" if mk_direction_up else "strong_downtrend"
        elif abs_pp > 0.3:
            label = "mild_uptrend" if mk_direction_up else "mild_downtrend"
        else:
            label = "stable"
        return label, f"gate4:percent_thresholds(pp12obs={pp:+.4f}pp)"
    else:
        # For USD/number series: use % change thresholds
        if pct_12obs > 10:
            label = "strong_uptrend"
        elif pct_12obs > 3:
            label = "mild_uptrend"
        elif pct_12obs < -10:
            label = "strong_downtrend"
        elif pct_12obs < -3:
            label = "mild_downtrend"
        else:
            label = "stable"
        return label, f"gate4:usd_number_thresholds(pct12obs={pct_12obs:.2f}%)"


# ---------------------------------------------------------------------------
# 4. Run and print results
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 120)
    print("TREND DETECTION SPIKE — Real Data Analysis")
    print(f"Lookback window: 24 months from latest observation per series")
    print("=" * 120)
    print()

    series_list = load_series_list()
    print(f"Found {len(series_list)} series in database.\n")

    results: list[dict] = []
    skipped: list[str] = []

    for series_meta in series_list:
        series_key = series_meta["series_key"]
        observations = load_observations(series_key)

        result = run_trend_analysis(series_key, observations, lookback_months=24)
        if result is None:
            skipped.append(series_key)
            continue

        result["title"] = series_meta["title"]
        result["source"] = series_meta["source_name"]
        results.append(result)

    # --- Print detailed results ---
    print("-" * 150)
    print(
        f"{'Series':<55} {'Label':<18} {'MK trend':<12} {'p-val':<9} {'Tau':<8} "
        f"{'%12obs':>8} {'pp12obs':>8} {'%6obs':>8} {'%3obs':>8} {'Slope%':>8} {'Dir':>5} {'#':>3}"
    )
    print("-" * 150)

    for r in sorted(results, key=lambda x: x["trend_label"]):
        short_key = r["series_key"]
        if len(short_key) > 53:
            short_key = short_key[:50] + "..."
        pp_str = f"{r['pp_12obs']:+.2f}" if r.get("pp_12obs") is not None else "N/A"
        print(
            f"{short_key:<55} "
            f"{r['trend_label']:<18} "
            f"{r['mk_trend']:<12} "
            f"{r['mk_p']:<9.4f} "
            f"{r['mk_tau']:<8.4f} "
            f"{str(r['pct_12obs']) if r['pct_12obs'] is not None else 'N/A':>8} "
            f"{pp_str:>8} "
            f"{str(r['pct_6obs']) if r['pct_6obs'] is not None else 'N/A':>8} "
            f"{str(r['pct_3obs']) if r['pct_3obs'] is not None else 'N/A':>8} "
            f"{r['recent_half_slope_pct']:>8.3f} "
            f"{r['consec_dir']:>5} "
            f"{r['consec_count']:>3}"
        )

    # --- Summary by label ---
    print()
    print("=" * 80)
    print("SUMMARY BY TREND LABEL")
    print("=" * 80)
    from collections import Counter

    label_counts = Counter(r["trend_label"] for r in results)
    for label in [
        "strong_uptrend",
        "mild_uptrend",
        "stable",
        "mild_downtrend",
        "strong_downtrend",
    ]:
        count = label_counts.get(label, 0)
        pct = count / len(results) * 100 if results else 0
        print(f"  {label:<20}: {count:>3} series  ({pct:>5.1f}%)")
    print(f"  {'TOTAL':<20}: {len(results):>3} series")
    print(f"  {'Skipped (< 10 obs)':<20}: {len(skipped):>3} series")

    # --- Group by source ---
    print()
    print("=" * 80)
    print("DETAILED RESULTS BY SOURCE")
    print("=" * 80)
    by_source: dict[str, list[dict]] = {}
    for r in results:
        by_source.setdefault(r["source"], []).append(r)

    for source_name, source_results in sorted(by_source.items()):
        print(f"\n  --- {source_name} ({len(source_results)} series) ---")
        for r in sorted(source_results, key=lambda x: x["series_key"]):
            mk_sig = "SIG" if r["mk_p"] < 0.05 else "n/s"
            momentum = (
                f"{r['consec_dir']}×{r['consec_count']}"
                if r["consec_count"] >= 3
                else "—"
            )
            pct_str = (
                f"Δ12obs:{r['pct_12obs']}%"
                if r["pct_12obs"] is not None
                else "Δ12obs:N/A"
            )
            print(
                f"    {r['series_key']:<52} "
                f"→ {r['trend_label']:<18} "
                f"[MK:{mk_sig} τ={r['mk_tau']:+.3f}] "
                f"[{pct_str}] "
                f"[slope2nd:{r['recent_half_slope_pct']:+.3f}%/obs] "
                f"[momentum:{momentum}]"
            )
            print(f"      {r['title']}")
            print(
                f"      Window: {r['window_start']} → {r['window_end']} ({r['obs_count_window']} obs in window, {r['obs_count_total']} total)"
            )
            print(f"      Gate: {r['gate_notes']}")

    # --- Gate rejection analysis ---
    print()
    print("=" * 80)
    print("GATE REJECTION ANALYSIS")
    print("=" * 80)
    stable_results = [r for r in results if r["trend_label"] == "stable"]
    non_stable = [r for r in results if r["trend_label"] != "stable"]
    print(f"  Series flagged with a trend: {len(non_stable)} of {len(results)}")
    print(f"  Series classified as stable: {len(stable_results)} of {len(results)}")
    print()

    # Count rejections by gate
    gate_counts: dict[str, int] = {}
    for r in stable_results:
        gate = r["gate_notes"].split(":")[0] if r["gate_notes"] else "unknown"
        gate_counts[gate] = gate_counts.get(gate, 0) + 1
    print("  Rejections by gate:")
    for gate, count in sorted(gate_counts.items()):
        print(f"    {gate}: {count} series")

    # Show gate details for rejected series that had significant MK
    rejected_with_sig_mk = [
        r for r in stable_results if r["mk_p"] < 0.05 and abs(r["mk_tau"]) >= 0.1
    ]
    if rejected_with_sig_mk:
        print(
            f"\n  Series with significant MK but rejected by later gates ({len(rejected_with_sig_mk)}):"
        )
        for r in rejected_with_sig_mk:
            print(
                f"    {r['series_key']:<52} "
                f"MK:{r['mk_trend']} τ={r['mk_tau']:+.3f} "
                f"Δ12obs%={r['pct_12obs']} "
                f"consec={r['consec_dir']}×{r['consec_count']} "
                f"slope2nd={r['recent_half_slope_pct']:+.3f}%"
            )
            print(f"      Rejected by: {r['gate_notes']}")

    # Overall assessment
    print()
    print("  False-positive risk assessment:")
    weak_signals = [r for r in non_stable if abs(r.get("pct_12obs") or 0) < 1]
    if weak_signals:
        print(f"    ⚠ {len(weak_signals)} trend-labeled series with |12m%| < 1:")
        for r in weak_signals:
            print(
                f"      {r['series_key']}: label={r['trend_label']}, Δ12obs%={r['pct_12obs']}"
            )
    else:
        print(
            "    ✓ All trend-labeled series have |Δ12obs%| >= 1 — no weak magnitude signals."
        )


if __name__ == "__main__":
    main()
