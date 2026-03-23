"""Series catalog primitives for grouped and split source ownership."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SeriesCatalogEntry:
    """One series item and its provider-level ownership metadata."""

    source_key: str
    provider_group_key: str
    series_item_key: str
    canonical_series_key: str
    ownership_mode: str = "grouped"


def validate_series_catalog_entries(entries: list[SeriesCatalogEntry]) -> None:
    """Validate series catalog invariants used by runtime wiring."""
    seen_series_item_keys: set[str] = set()
    seen_canonical_series_keys: set[str] = set()

    for entry in entries:
        if not entry.source_key.strip():
            raise ValueError("series catalog entry source_key must be non-empty")
        if not entry.provider_group_key.strip():
            raise ValueError("series catalog entry provider_group_key must be non-empty")
        if not entry.series_item_key.strip():
            raise ValueError("series catalog entry series_item_key must be non-empty")
        if not entry.canonical_series_key.strip():
            raise ValueError("series catalog entry canonical_series_key must be non-empty")
        if entry.ownership_mode not in {"grouped", "split"}:
            raise ValueError("series catalog entry ownership_mode must be grouped or split")

        if entry.series_item_key in seen_series_item_keys:
            raise ValueError(
                f"duplicate series_item_key in series catalog: {entry.series_item_key}"
            )
        seen_series_item_keys.add(entry.series_item_key)

        if entry.canonical_series_key in seen_canonical_series_keys:
            raise ValueError(
                f"duplicate canonical_series_key in series catalog: {entry.canonical_series_key}"
            )
        seen_canonical_series_keys.add(entry.canonical_series_key)
