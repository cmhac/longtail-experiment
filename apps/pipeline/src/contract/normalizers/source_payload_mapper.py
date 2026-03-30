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


def _normalize_unit_type(raw: object) -> str | None:
    if not isinstance(raw, str):
        return None
    normalized = raw.strip().lower()
    if normalized in {"usd", "percent", "number"}:
        return normalized
    return None


def _infer_unit_type_from_unit_label(raw: object) -> str | None:
    if not isinstance(raw, str):
        return None
    normalized = raw.strip().lower()
    if normalized == "":
        return None
    if "%" in normalized or "percent" in normalized:
        return "percent"
    if "$" in normalized or "dollar" in normalized:
        return "usd"
    return "number"


def _coerce_attributes(raw: object) -> dict[str, str]:
    if not isinstance(raw, dict):
        return {}
    coerced: dict[str, str] = {}
    for key, value in raw.items():
        coerced[str(key)] = str(value)
    return coerced


def normalize_source_payload(payload: dict[str, object]) -> CanonicalObservation:
    """Map variant source payload keys into the canonical observation schema."""
    source_type = str(payload["source_type"]).strip().lower()
    topic_tags = _coerce_topic_tags(payload.get("topic_tags") or payload.get("tags"))
    unit_value = payload.get("unit")
    unit_type = _normalize_unit_type(payload.get("unit_type")) or _infer_unit_type_from_unit_label(
        unit_value
    )
    attributes = _coerce_attributes(payload.get("attributes") or {})
    if unit_type is not None:
        attributes["unit_type"] = unit_type

    return CanonicalObservation.model_validate(
        {
            "source_key": str(payload["source_key"]),
            "source_name": str(payload["source_name"]),
            "source_title": str(payload["source_title"]),
            "source_description": str(payload["source_description"]),
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
            "unit": unit_value,
            "unit_type": unit_type,
            "attributes": attributes,
        }
    )
