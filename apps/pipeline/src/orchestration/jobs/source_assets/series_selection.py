"""Helpers for resolving series-item targeted trigger requests."""

from __future__ import annotations

from dataclasses import dataclass

from .series_catalog import SeriesCatalogEntry


@dataclass(frozen=True)
class SeriesSelectionResolution:
    """Resolved source and series selection after validating trigger tags."""

    selected_source_keys: list[str] | None
    selected_series_item_keys: list[str] | None
    invalid_series_item_keys: list[str]


def normalize_requested_series_item_keys(
    *,
    series_item_key_tag: str | None,
    series_item_keys_tag: str | None,
) -> list[str] | None:
    """Normalize series selection tags into sorted unique series item keys."""
    raw: list[str] = []
    if series_item_key_tag is not None and series_item_key_tag.strip():
        raw.append(series_item_key_tag)
    if series_item_keys_tag is not None and series_item_keys_tag.strip():
        raw.extend(series_item_keys_tag.split(","))

    normalized = sorted({item.strip() for item in raw if item.strip()})
    if not normalized:
        return None
    return normalized


def resolve_series_selection(
    *,
    requested_series_item_keys: list[str] | None,
    catalog_entries: tuple[object, ...] | list[object],
    selected_source_keys: list[str] | None,
) -> SeriesSelectionResolution:
    """Resolve series-targeted requests into source and series execution scope."""
    if requested_series_item_keys is None:
        return SeriesSelectionResolution(
            selected_source_keys=selected_source_keys,
            selected_series_item_keys=None,
            invalid_series_item_keys=[],
        )

    by_series_key: dict[str, SeriesCatalogEntry] = {}
    for entry in catalog_entries:
        if isinstance(entry, SeriesCatalogEntry):
            by_series_key[entry.series_item_key] = entry

    invalid = [key for key in requested_series_item_keys if key not in by_series_key]
    valid_entries = [
        by_series_key[key] for key in requested_series_item_keys if key in by_series_key
    ]
    if selected_source_keys is None:
        derived_source_keys = sorted({entry.source_key for entry in valid_entries})
    else:
        selected_set = set(selected_source_keys)
        derived_source_keys = sorted(
            {entry.source_key for entry in valid_entries if entry.source_key in selected_set}
        )

    return SeriesSelectionResolution(
        selected_source_keys=derived_source_keys,
        selected_series_item_keys=sorted({entry.series_item_key for entry in valid_entries}),
        invalid_series_item_keys=invalid,
    )
