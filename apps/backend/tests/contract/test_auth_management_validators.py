"""Unit coverage for auth/account input validators."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.contract.errors import ContractQueryError
from src.query.auth_management_validators import (
    ensure_account_active,
    normalize_display_name,
    normalize_email,
    normalize_optional_email,
    parse_lockout_until,
    validate_password_strength,
)


def test_normalize_email_validates_and_lowercases() -> None:
    """Normalize email values and reject invalid inputs."""
    assert normalize_email(" User@Example.COM ") == "user@example.com"

    with pytest.raises(ContractQueryError):
        normalize_email("invalid")


def test_normalize_optional_email_passthrough_and_validation() -> None:
    """Normalize optional email or reject invalid optional email strings."""
    assert normalize_optional_email(None) is None
    assert normalize_optional_email(" User@Example.COM ") == "user@example.com"

    with pytest.raises(ContractQueryError):
        normalize_optional_email("invalid")


def test_normalize_display_name_handles_empty_and_max_length() -> None:
    """Normalize optional display names and enforce max length."""
    assert normalize_display_name("  Example User  ") == "Example User"
    assert normalize_display_name(" ") is None
    assert normalize_display_name(None) is None

    with pytest.raises(ContractQueryError):
        normalize_display_name("x" * 256)


def test_password_strength_and_lockout_parsing() -> None:
    """Enforce minimum password length and parse lockout timestamps."""
    validate_password_strength("verysecure123")

    with pytest.raises(ContractQueryError):
        validate_password_strength("short")

    parsed = parse_lockout_until("2026-04-02T00:00:00+00:00")
    assert parsed == datetime(2026, 4, 2, tzinfo=UTC)
    assert parse_lockout_until(None) is None

    with pytest.raises(ContractQueryError):
        parse_lockout_until("not-a-date")


def test_ensure_account_active_rejects_non_active_states() -> None:
    """Allow active accounts and reject deactivated/deletion lifecycle states."""
    ensure_account_active("active")

    with pytest.raises(ContractQueryError):
        ensure_account_active("deactivated")
