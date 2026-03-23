"""Validation helpers for dataset discovery request inputs."""

from __future__ import annotations

from datetime import date

from src.contract.errors import ContractQueryError

_DEFAULT_PAGE = 1
_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100
_MAX_RECENT_LIMIT = 5


def normalize_page(page: int | None) -> int:
    """Normalize page input and enforce minimum value."""
    resolved = _DEFAULT_PAGE if page is None else int(page)
    if resolved < 1:
        raise ContractQueryError("page must be greater than or equal to 1")
    return resolved


def normalize_page_size(page_size: int | None) -> int:
    """Normalize page size input and enforce configured bounds."""
    resolved = _DEFAULT_PAGE_SIZE if page_size is None else int(page_size)
    if resolved < 1 or resolved > _MAX_PAGE_SIZE:
        raise ContractQueryError("page_size must be between 1 and 100")
    return resolved


def normalize_recent_limit(limit: int | None) -> int:
    """Normalize recent updates limit and enforce contract maximum."""
    resolved = _MAX_RECENT_LIMIT if limit is None else int(limit)
    if resolved < 1 or resolved > _MAX_RECENT_LIMIT:
        raise ContractQueryError("limit must be between 1 and 5")
    return resolved


def normalize_query_text(query_text: str | None) -> str | None:
    """Trim incoming query text and collapse empty values to None."""
    if query_text is None:
        return None
    normalized = query_text.strip()
    return normalized or None


def parse_optional_date(value: str | date | None, *, field_name: str) -> date | None:
    """Parse optional ISO date value used by detail range filters."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise ContractQueryError(f"{field_name} must be a valid ISO date") from exc


def validate_date_range(from_date: date | None, to_date: date | None) -> None:
    """Ensure optional date range values are ordered if both are present."""
    if from_date is not None and to_date is not None and from_date > to_date:
        raise ContractQueryError("from_date must be on or before to_date")
