"""Trend span normalization for dataset detail rendering payloads."""

from __future__ import annotations

from datetime import date
from typing import Any


def _to_date(value: object, *, field_name: str) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value.strip():
        return date.fromisoformat(value)
    raise ValueError(f"invalid trend span {field_name}")


def normalize_trend_spans(raw_spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize trend spans to deterministic non-overlapping intervals."""
    projected: list[dict[str, Any]] = []
    for row in raw_spans:
        start_period = _to_date(row.get("start_period"), field_name="start_period")
        end_period = _to_date(row.get("end_period"), field_name="end_period")
        if end_period < start_period:
            raise ValueError("invalid trend span period order")

        direction = str(row.get("direction", "")).strip().lower()
        if direction not in {"up", "down"}:
            raise ValueError("invalid trend span direction")

        tooltip_value = row.get("tooltip")
        if not isinstance(tooltip_value, dict):
            raise ValueError("invalid trend span tooltip")

        projected.append(
            {
                "_start_date": start_period,
                "_end_date": end_period,
                "direction": direction,
                "trend_label": str(row.get("trend_label", "")).strip() or "trend_event",
                "tooltip": {
                    "headline": str(tooltip_value.get("headline", "")).strip(),
                    "detail": str(tooltip_value.get("detail", "")).strip(),
                },
            }
        )

    projected.sort(
        key=lambda item: (
            item["_start_date"],
            item["_end_date"],
            item["trend_label"],
        )
    )

    normalized: list[dict[str, Any]] = []
    for span in projected:
        if not normalized:
            normalized.append(span)
            continue

        candidate = span
        previous = normalized[-1]
        if candidate["_start_date"] <= previous["_end_date"]:
            candidate = dict(candidate)
            candidate["_start_date"] = previous["_end_date"]
            if candidate["_start_date"] > candidate["_end_date"]:
                continue
        normalized.append(candidate)

    return [
        {
            "start_period": span["_start_date"].isoformat(),
            "end_period": span["_end_date"].isoformat(),
            "direction": span["direction"],
            "trend_label": span["trend_label"],
            "tooltip": span["tooltip"],
        }
        for span in normalized
    ]
