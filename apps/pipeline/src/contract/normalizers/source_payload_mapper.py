"""Source payload normalization for canonical observation ingestion."""

from __future__ import annotations

from src.contract.schemas.canonical_observation import CanonicalObservation


def _coerce_topic_tags(raw: object) -> list[str]:
    """Coerce mixed tag payloads into trimmed string tag lists."""
    if not isinstance(raw, list):
        return []
    coerced: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            continue
        value = item.strip()
        if value:
            coerced.append(value)
    return coerced


def normalize_source_payload(payload: dict[str, object]) -> CanonicalObservation:
    """Map variant source payload keys into the canonical observation schema."""
    source_type = str(payload["source_type"]).strip().lower()
    topic_tags = _coerce_topic_tags(payload.get("topic_tags") or payload.get("tags"))

    return CanonicalObservation.model_validate(
        {
            "source_name": str(payload["source_name"]),
            "source_type": source_type,
            "series_key": str(payload["series_key"]),
            "metric_name": str(payload["metric_name"]),
            "dataset_title": payload.get("dataset_title") or payload.get("title"),
            "dataset_description": payload.get("dataset_description") or payload.get("description"),
            "dataset_geographic_scope": payload.get("dataset_geographic_scope")
            or payload.get("geographic_scope"),
            "topic_tags": topic_tags,
            "observed_on": payload.get("date") or payload.get("observed_on"),
            "reported_at": payload["reported_at"],
            "value": payload["value"],
            "unit": payload.get("unit"),
            "attributes": payload.get("attributes") or {},
        }
    )
