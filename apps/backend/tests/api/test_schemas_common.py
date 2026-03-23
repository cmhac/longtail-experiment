"""Tests for PaginatedResponse, ErrorResponse, and HealthResponse schemas."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.api.schemas.common import ErrorResponse, HealthResponse, PaginatedResponse

# --- PaginatedResponse ---


def test_paginated_response_valid() -> None:
    """PaginatedResponse accepts valid inputs."""
    r = PaginatedResponse[str](items=["a", "b"], total=2, page=1, page_size=50)
    assert r.total == 2
    assert r.page == 1
    assert r.page_size == 50
    assert r.items == ["a", "b"]


def test_paginated_response_empty_items() -> None:
    """PaginatedResponse with empty items and zero total is valid."""
    r = PaginatedResponse[str](items=[], total=0, page=1, page_size=50)
    assert r.total == 0
    assert r.items == []


def test_paginated_response_rejects_negative_total() -> None:
    """PaginatedResponse rejects negative total."""
    with pytest.raises(ValidationError):
        PaginatedResponse[str](items=[], total=-1, page=1, page_size=50)


def test_paginated_response_rejects_page_zero() -> None:
    """PaginatedResponse rejects page=0."""
    with pytest.raises(ValidationError):
        PaginatedResponse[str](items=[], total=0, page=0, page_size=50)


def test_paginated_response_rejects_page_size_zero() -> None:
    """PaginatedResponse rejects page_size=0."""
    with pytest.raises(ValidationError):
        PaginatedResponse[str](items=[], total=0, page=1, page_size=0)


def test_paginated_response_rejects_page_size_over_max() -> None:
    """PaginatedResponse rejects page_size > 200."""
    with pytest.raises(ValidationError):
        PaginatedResponse[str](items=[], total=0, page=1, page_size=201)


def test_paginated_response_max_page_size_accepted() -> None:
    """PaginatedResponse accepts page_size=200."""
    r = PaginatedResponse[str](items=[], total=0, page=1, page_size=200)
    assert r.page_size == 200


# --- ErrorResponse ---


def test_error_response_valid() -> None:
    """ErrorResponse accepts valid inputs."""
    r = ErrorResponse(code="not_found", message="Resource not found")
    assert r.code == "not_found"
    assert r.details is None
    assert r.correlation_id is None


def test_error_response_with_details() -> None:
    """ErrorResponse accepts details and correlation_id."""
    r = ErrorResponse(
        code="validation_error",
        message="Bad input",
        details={"field": "page"},
        correlation_id="abc-123",
    )
    assert r.details == {"field": "page"}
    assert r.correlation_id == "abc-123"


def test_error_response_rejects_empty_code() -> None:
    """ErrorResponse rejects empty code."""
    with pytest.raises(ValidationError):
        ErrorResponse(code="", message="msg")


def test_error_response_rejects_empty_message() -> None:
    """ErrorResponse rejects empty message."""
    with pytest.raises(ValidationError):
        ErrorResponse(code="err", message="")


# --- HealthResponse ---


def test_health_response_ok() -> None:
    """HealthResponse accepts ok/reachable."""
    r = HealthResponse(status="ok", db="reachable")
    assert r.status == "ok"
    assert r.db == "reachable"


def test_health_response_degraded() -> None:
    """HealthResponse accepts degraded/unreachable."""
    r = HealthResponse(status="degraded", db="unreachable")
    assert r.status == "degraded"
    assert r.db == "unreachable"


def test_health_response_rejects_invalid_db() -> None:
    """HealthResponse rejects invalid db value."""
    with pytest.raises(ValidationError):
        HealthResponse(status="ok", db="unknown")


def test_health_response_rejects_empty_status() -> None:
    """HealthResponse rejects empty status."""
    with pytest.raises(ValidationError):
        HealthResponse(status="", db="reachable")
