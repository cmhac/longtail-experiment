"""Ownership-mode validation and lookup helpers for series items."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

OwnershipMode = Literal["grouped", "split"]
MIN_DATETIME_UTC = datetime.min.replace(tzinfo=UTC)


@dataclass(frozen=True)
class SeriesOwnershipModeRecord:
    """One ownership declaration window for a series item."""

    series_item_key: str
    owner_adapter_key: str
    mode: OwnershipMode
    effective_from: datetime | None = None
    effective_to: datetime | None = None


def is_record_active(
    record: SeriesOwnershipModeRecord,
    *,
    evaluated_at: datetime,
) -> bool:
    """Return whether one ownership record is active at the evaluation timestamp."""
    if record.effective_from is not None and evaluated_at < record.effective_from:
        return False
    return not (record.effective_to is not None and evaluated_at >= record.effective_to)


def resolve_schedule_authority_owner(
    *,
    series_item_key: str,
    ownership_mode_registry: dict[str, SeriesOwnershipModeRecord],
    evaluated_at: datetime,
) -> str | None:
    """Resolve authoritative owner adapter key for one series at a timestamp."""
    record = ownership_mode_registry.get(series_item_key)
    if record is None:
        return None
    if not is_record_active(record, evaluated_at=evaluated_at):
        return None
    return record.owner_adapter_key


def validate_ownership_mode_windows(records: list[SeriesOwnershipModeRecord]) -> None:
    """Reject overlapping ownership windows for the same series item."""
    by_series: dict[str, list[SeriesOwnershipModeRecord]] = {}
    for record in records:
        if not record.series_item_key.strip():
            raise ValueError("ownership mode series_item_key must be non-empty")
        if not record.owner_adapter_key.strip():
            raise ValueError("ownership mode owner_adapter_key must be non-empty")
        by_series.setdefault(record.series_item_key, []).append(record)

    for series_item_key, series_records in by_series.items():
        sorted_records = sorted(
            series_records,
            key=lambda value: value.effective_from or MIN_DATETIME_UTC,
        )
        for index in range(1, len(sorted_records)):
            previous = sorted_records[index - 1]
            current = sorted_records[index]
            if previous.effective_to is None:
                raise ValueError(
                    f"overlapping ownership windows for series_item_key={series_item_key}"
                )
            if current.effective_from is None:
                raise ValueError(
                    f"overlapping ownership windows for series_item_key={series_item_key}"
                )
            if current.effective_from < previous.effective_to:
                raise ValueError(
                    f"overlapping ownership windows for series_item_key={series_item_key}"
                )


def build_ownership_mode_registry(
    records: list[SeriesOwnershipModeRecord],
) -> dict[str, SeriesOwnershipModeRecord]:
    """Build fast lookup for active ownership mode by series item key."""
    validate_ownership_mode_windows(records)
    latest_by_series: dict[str, SeriesOwnershipModeRecord] = {}
    for record in records:
        current = latest_by_series.get(record.series_item_key)
        if current is None:
            latest_by_series[record.series_item_key] = record
            continue
        current_from = current.effective_from or MIN_DATETIME_UTC
        record_from = record.effective_from or MIN_DATETIME_UTC
        if record_from >= current_from:
            latest_by_series[record.series_item_key] = record
    return latest_by_series
