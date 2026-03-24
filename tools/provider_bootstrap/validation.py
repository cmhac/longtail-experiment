"""Validation helpers for provider bootstrap command."""

from __future__ import annotations

import re

VALID_CADENCE_LABELS = {"hourly", "daily", "weekly", "monthly", "custom_interval"}
VALID_OWNERSHIP_MODES = {"grouped", "split"}

_SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
_CANONICAL_KEY_PATTERN = re.compile(r"^[A-Z0-9]+(?:\.[A-Z0-9_]+){1,}$")
_CRON_TOKEN_PATTERN = re.compile(r"^[\d*/,-]+$")


def validate_snake_identifier(name: str, *, field: str) -> None:
    if not _SNAKE_CASE_PATTERN.fullmatch(name):
        raise ValueError(f"{field} must be snake_case using lowercase letters, numbers, and underscores")


def normalize_module_name(module_name: str) -> str:
    """Return module stem normalized to *_source format."""
    stem = module_name.replace(".py", "").strip()
    validate_snake_identifier(stem, field="module_name")
    if not stem.endswith("_source"):
        stem = f"{stem}_source"
    return stem


def validate_cadence_label(cadence_label: str) -> None:
    if cadence_label not in VALID_CADENCE_LABELS:
        values = ", ".join(sorted(VALID_CADENCE_LABELS))
        raise ValueError(f"cadence_label must be one of: {values}")


def validate_ownership_mode(ownership_mode: str) -> None:
    if ownership_mode not in VALID_OWNERSHIP_MODES:
        values = ", ".join(sorted(VALID_OWNERSHIP_MODES))
        raise ValueError(f"ownership_mode must be one of: {values}")


def validate_cron_schedule(cron_schedule: str) -> None:
    parts = cron_schedule.split()
    if len(parts) != 5:
        raise ValueError("cron_schedule must contain exactly 5 cron fields")
    for token in parts:
        if not _CRON_TOKEN_PATTERN.fullmatch(token):
            raise ValueError(
                "cron_schedule contains invalid token; allowed chars are digits, '*', '/', '-', ','",
            )


def validate_canonical_key(canonical_key: str) -> None:
    if not _CANONICAL_KEY_PATTERN.fullmatch(canonical_key):
        raise ValueError(
            "canonical_series_key must be uppercase dotted format like CATEGORY.COUNTRY.SERIES",
        )


def validate_series_alignment(
    *,
    series_item_keys: list[str],
    canonical_series_keys: list[str],
    provider_series_ids: list[str],
) -> None:
    count = len(series_item_keys)
    if count == 0:
        raise ValueError("at least one --series-item-key is required")
    if count != len(canonical_series_keys) or count != len(provider_series_ids):
        raise ValueError(
            "series_item_keys, canonical_series_keys, and provider_series_ids must have matching counts",
        )
