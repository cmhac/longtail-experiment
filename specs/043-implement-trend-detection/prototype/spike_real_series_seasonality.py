"""Spike: run seasonality-aware trend detection on a real local-dev series.

This script intentionally validates local runtime prerequisites before analysis:
1) Backend API server must be reachable (dev server running)
2) Local Postgres must be reachable
3) Target series must exist and contain observations (ingestion has run)

Target series defaults to ENERGY.US.RETAIL_GASOLINE.SCO.

Usage:
    apps/backend/.venv/bin/python research_trend_detection/spike_real_series_seasonality.py
"""

from __future__ import annotations

import json
from datetime import date
from statistics import median
from typing import Literal
from urllib.error import URLError
from urllib.request import urlopen

import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from spike_multi_horizon import (
    MultiHorizonResult,
    SyntheticSeries,
    analyze_series,
)

SERIES_KEY = "ENERGY.US.RETAIL_GASOLINE.SCO"
BACKEND_HEALTH_URL = "http://127.0.0.1:8080/api/health"
DATABASE_URL = "postgresql+psycopg://longtail:longtail@127.0.0.1:55432/longtail_local"

Cadence = Literal["daily", "weekly", "monthly"]

SERIES_META_QUERY = text(
    """
    SELECT
        ds.series_key,
        ds.title,
        sp.source_name
    FROM data_series ds
    JOIN source_profiles sp ON sp.id = ds.source_profile_id
    WHERE ds.series_key = :series_key
    """
)

OBS_QUERY = text(
    """
    SELECT o.observed_on, o.value, o.attributes
    FROM observations o
    JOIN data_series ds ON ds.id = o.series_id
    WHERE ds.series_key = :series_key
    ORDER BY o.observed_on ASC
    """
)


def fail(message: str) -> None:
    """Exit with a hard failure and a clear remediation message."""
    print(f"ERROR: {message}")
    raise SystemExit(1)


def check_backend_health() -> None:
    """Require the local backend dev server to be running."""
    try:
        with urlopen(BACKEND_HEALTH_URL, timeout=2) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except URLError:
        fail(
            "Local backend dev server is not reachable at "
            f"{BACKEND_HEALTH_URL}. Start local services first, e.g. "
            "`docker compose up -d db backend`."
        )
    except (TimeoutError, json.JSONDecodeError):
        fail(
            "Backend health endpoint did not return a valid response. "
            "Verify local backend is running (`docker compose ps backend`)."
        )

    if payload.get("status") != "ok":
        fail(
            "Backend health endpoint returned a non-ok status. "
            "Check logs with `docker compose logs backend`."
        )


def infer_cadence(observed_on: list[date]) -> Cadence:
    """Infer cadence from median day gap between observations."""
    if len(observed_on) < 3:
        fail("Not enough observations to infer cadence (need at least 3 records).")

    gaps = [
        (observed_on[i + 1] - observed_on[i]).days for i in range(len(observed_on) - 1)
    ]
    med_gap = median(gaps)

    if med_gap <= 2:
        return "daily"
    if med_gap <= 10:
        return "weekly"
    return "monthly"


def infer_unit_type(attributes: list[dict]) -> str:
    """Infer series unit_type in the same shape used by the spike classifier."""
    for attr in reversed(attributes):
        unit_type = attr.get("unit_type")
        if unit_type in {"usd", "percent", "number"}:
            return str(unit_type)

    return "number"


def load_real_series() -> SyntheticSeries:
    """Load the target series from local Postgres and map it to SyntheticSeries."""
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    try:
        with engine.connect() as conn:
            meta = (
                conn.execute(SERIES_META_QUERY, {"series_key": SERIES_KEY})
                .mappings()
                .first()
            )
            if meta is None:
                fail(
                    f"Series {SERIES_KEY} was not found in local database. "
                    "Run local ingestion first."
                )

            rows = conn.execute(OBS_QUERY, {"series_key": SERIES_KEY}).mappings().all()
    except SQLAlchemyError as exc:
        fail(
            "Unable to query local Postgres at 127.0.0.1:55432. "
            "Ensure local DB is running (`docker compose up -d db`). "
            f"Original error: {exc}"
        )

    if not rows:
        fail(
            f"Series {SERIES_KEY} has no observations. "
            "Run local Dagster ingestion/materialization first, then retry."
        )

    observed_on = [r["observed_on"] for r in rows]
    values = np.array([float(r["value"]) for r in rows], dtype=float)
    attributes = [r["attributes"] or {} for r in rows]

    cadence = infer_cadence(observed_on)
    unit_type = infer_unit_type(attributes)

    return SyntheticSeries(
        name=str(meta["series_key"]),
        description=(f"{meta['title']} ({meta['source_name']}) — real local-dev data"),
        expected_label="n/a",
        cadence=cadence,
        unit_type=unit_type,
        dates=observed_on,
        values=values,
    )


def print_result(series: SyntheticSeries, result: MultiHorizonResult) -> None:
    """Print analysis output for the target real series."""
    print("=" * 100)
    print("REAL-DATA SEASONALITY SPIKE")
    print("=" * 100)
    print(f"Series:        {series.name}")
    print(f"Description:   {series.description}")
    print(f"Cadence:       {result.cadence}")
    print(f"Unit type:     {result.unit_type}")
    print(f"Observations:  {result.obs_count}")
    print(f"Trend label:   {result.trend_label}")
    print(f"Reason:        {result.classification_reason}")

    if result.seasonality_info:
        info = result.seasonality_info
        seasonal_text = "SEASONAL" if info.is_seasonal else "non-seasonal"
        suffix = "" if info.enough_data else " (insufficient data for full detection)"
        print(
            "Seasonality:   "
            f"{seasonal_text} "
            f"(Fs={info.fs_score:.3f}, "
            f"ACF={info.acf_at_period:.3f}, "
            f"Spectral={info.spectral_ratio:.2f}, "
            f"period={info.period}){suffix}"
        )

    print()
    print("Window Results:")
    for wr in result.window_results:
        sig = "SIG" if wr.significant else "n/s"
        pct = "N/A" if wr.pct_change is None else f"{wr.pct_change:+.2f}%"
        pp = "N/A" if wr.pp_change is None else f"{wr.pp_change:+.4f}pp"
        print(
            f"  {wr.window_name:<5} {wr.obs_count:>4} obs [{sig}] "
            f"p={wr.mk_p:<8.4f} τ={wr.mk_tau:+.3f} Δ%={pct:<10} Δpp={pp}"
        )


def main() -> None:
    check_backend_health()
    series = load_real_series()
    result = analyze_series(series)
    print_result(series, result)


if __name__ == "__main__":
    main()
