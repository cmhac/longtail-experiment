"""Source payload normalization for canonical observation ingestion."""

from __future__ import annotations

from src.contract.schemas.canonical_observation import CanonicalObservation

_FREQUENCY_MAP = {
    "d": "daily",
    "daily": "daily",
    "w": "weekly",
    "weekly": "weekly",
    "m": "monthly",
    "monthly": "monthly",
    "q": "quarterly",
    "quarterly": "quarterly",
    "y": "yearly",
    "yearly": "yearly",
}


def normalize_source_payload(payload: dict[str, object]) -> CanonicalObservation:
    """Map variant source payload keys into the canonical observation schema."""
    frequency_raw = str(payload.get("frequency") or payload.get("frequency_granularity") or "")
    normalized_frequency = frequency_raw.strip().lower()
    canonical_frequency = _FREQUENCY_MAP.get(normalized_frequency, normalized_frequency)
    source_type = str(payload["source_type"]).strip().lower()

    return CanonicalObservation.model_validate(
        {
            "source_name": str(payload["source_name"]),
            "source_type": source_type,
            "series_key": str(payload["series_key"]),
            "metric_name": str(payload["metric_name"]),
            "frequency_granularity": canonical_frequency,
            "observed_on": payload.get("date") or payload.get("observed_on"),
            "reported_at": payload["reported_at"],
            "value": payload["value"],
            "unit": payload.get("unit"),
            "attributes": payload.get("attributes") or {},
        }
    )
