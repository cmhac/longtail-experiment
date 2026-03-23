"""Ownership transition helpers for grouped/split schedule authority changes."""

from __future__ import annotations

from datetime import datetime

from .ownership_mode import (
    OwnershipMode,
    SeriesOwnershipModeRecord,
    validate_ownership_mode_windows,
)


def apply_ownership_transition(  # noqa: PLR0913
    *,
    existing_records: list[SeriesOwnershipModeRecord],
    series_item_key: str,
    new_owner_adapter_key: str,
    new_mode: OwnershipMode,
    effective_from: datetime,
    transition_reason: str | None = None,
) -> list[SeriesOwnershipModeRecord]:
    """Apply one ownership transition by closing prior active window then appending new record."""
    if new_mode not in {"grouped", "split"}:
        raise ValueError("new_mode must be grouped or split")

    updated: list[SeriesOwnershipModeRecord] = []
    for record in existing_records:
        if record.series_item_key != series_item_key:
            updated.append(record)
            continue
        if record.effective_to is None:
            updated.append(
                SeriesOwnershipModeRecord(
                    series_item_key=record.series_item_key,
                    owner_adapter_key=record.owner_adapter_key,
                    mode=record.mode,
                    effective_from=record.effective_from,
                    effective_to=effective_from,
                )
            )
            continue
        updated.append(record)

    updated.append(
        SeriesOwnershipModeRecord(
            series_item_key=series_item_key,
            owner_adapter_key=new_owner_adapter_key,
            mode=new_mode,
            effective_from=effective_from,
            effective_to=None,
        )
    )

    validate_ownership_mode_windows(updated)
    return updated
