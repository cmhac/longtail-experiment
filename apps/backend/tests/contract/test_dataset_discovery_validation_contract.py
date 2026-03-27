"""Contract tests for shared dataset discovery validation and error semantics."""

# ruff: noqa: D103

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.errors import ContractQueryError
from src.query.dataset_discovery_validators import (
    normalize_page,
    normalize_page_size,
    normalize_page_size_with_bounds,
    normalize_recent_limit,
    parse_optional_date,
    validate_date_range,
)

DEFAULT_PAGE_SIZE = 25
VALID_PAGE_SIZE = 40
MAX_PAGE_SIZE = 80


def test_dataset_discovery_validators_enforce_page_bounds() -> None:
    with pytest.raises(ContractQueryError):
        normalize_page(0)

    with pytest.raises(ContractQueryError):
        normalize_page_size(101)


def test_dataset_discovery_validators_enforce_recent_limit_bounds() -> None:
    with pytest.raises(ContractQueryError):
        normalize_recent_limit(0)

    with pytest.raises(ContractQueryError):
        normalize_recent_limit(6)


def test_dataset_discovery_validators_reject_inverted_date_ranges() -> None:
    from_date = parse_optional_date("2026-02-01", field_name="from_date")
    to_date = parse_optional_date("2026-01-01", field_name="to_date")

    with pytest.raises(ContractQueryError):
        validate_date_range(from_date, to_date)


def test_dataset_discovery_validators_support_route_level_page_size_bounds() -> None:
    assert (
        normalize_page_size_with_bounds(
            None,
            default_page_size=DEFAULT_PAGE_SIZE,
            max_page_size=MAX_PAGE_SIZE,
        )
        == DEFAULT_PAGE_SIZE
    )
    assert (
        normalize_page_size_with_bounds(
            VALID_PAGE_SIZE,
            default_page_size=DEFAULT_PAGE_SIZE,
            max_page_size=MAX_PAGE_SIZE,
        )
        == VALID_PAGE_SIZE
    )

    with pytest.raises(ContractQueryError):
        normalize_page_size_with_bounds(
            MAX_PAGE_SIZE + 1,
            default_page_size=DEFAULT_PAGE_SIZE,
            max_page_size=MAX_PAGE_SIZE,
        )
