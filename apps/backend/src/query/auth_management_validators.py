"""Validation helpers for auth/account request inputs."""

from __future__ import annotations

from datetime import UTC, datetime

from src.contract.errors import ContractQueryError

_MIN_PASSWORD_LENGTH = 12
_MAX_DISPLAY_NAME_LENGTH = 255


def normalize_email(value: str) -> str:
    """Normalize and validate email input."""
    normalized = value.strip().lower()
    if normalized == "" or "@" not in normalized:
        raise ContractQueryError("email must be a valid address")
    return normalized


def normalize_display_name(value: str | None) -> str | None:
    """Normalize optional display-name input with bounded length."""
    if value is None:
        return None
    normalized = value.strip()
    if normalized == "":
        return None
    if len(normalized) > _MAX_DISPLAY_NAME_LENGTH:
        raise ContractQueryError(
            f"display_name must be at most {_MAX_DISPLAY_NAME_LENGTH} characters"
        )
    return normalized


def normalize_optional_email(value: str | None) -> str | None:
    """Normalize optional email payload values for account profile updates."""
    if value is None:
        return None
    return normalize_email(value)


def validate_password_strength(value: str) -> None:
    """Validate baseline password requirements for initial auth release."""
    if len(value) < _MIN_PASSWORD_LENGTH:
        raise ContractQueryError("password must be at least 12 characters")


def parse_lockout_until(value: object) -> datetime | None:
    """Parse a persisted lockout timestamp from repository payloads."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(UTC)
    try:
        return datetime.fromisoformat(str(value)).astimezone(UTC)
    except ValueError as exc:
        raise ContractQueryError("lockout_until must be a valid ISO datetime") from exc


def ensure_account_active(account_status: str) -> None:
    """Ensure account status allows authenticated product access."""
    if account_status != "active":
        raise ContractQueryError("account is not active")
