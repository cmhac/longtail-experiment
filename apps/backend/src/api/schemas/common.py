"""Common response envelope schemas shared across all API endpoints."""

from __future__ import annotations

from pydantic import BaseModel, field_validator

_MAX_PAGE = 200


class PaginatedResponse[T](BaseModel):
    """Generic pagination envelope returned by all list endpoints."""

    items: list[T]
    total: int
    page: int
    page_size: int

    @field_validator("total")
    @classmethod
    def total_non_negative(cls, v: int) -> int:
        """Validate total is non-negative."""
        if v < 0:
            msg = "total must be non-negative"
            raise ValueError(msg)
        return v

    @field_validator("page")
    @classmethod
    def page_at_least_one(cls, v: int) -> int:
        """Validate page is at least 1."""
        if v < 1:
            msg = "page must be >= 1"
            raise ValueError(msg)
        return v

    @field_validator("page_size")
    @classmethod
    def page_size_in_range(cls, v: int) -> int:
        """Validate page_size is between 1 and 200."""
        if v < 1 or v > _MAX_PAGE:
            msg = f"page_size must be between 1 and {_MAX_PAGE}"
            raise ValueError(msg)
        return v


class ErrorResponse(BaseModel):
    """Structured error envelope returned by 4xx and 5xx responses."""

    code: str
    message: str
    details: dict | None = None
    correlation_id: str | None = None

    @field_validator("code", "message")
    @classmethod
    def non_empty_string(cls, v: str) -> str:
        """Validate that code and message are non-empty."""
        if not v or not v.strip():
            msg = "must be non-empty"
            raise ValueError(msg)
        return v


class HealthResponse(BaseModel):
    """Response shape for GET /health."""

    status: str
    db: str

    @field_validator("status")
    @classmethod
    def status_non_empty(cls, v: str) -> str:
        """Validate status is non-empty."""
        if not v or not v.strip():
            msg = "status must be non-empty"
            raise ValueError(msg)
        return v

    @field_validator("db")
    @classmethod
    def db_valid_value(cls, v: str) -> str:
        """Validate db is one of the allowed values."""
        if v not in ("reachable", "unreachable"):
            msg = "db must be 'reachable' or 'unreachable'"
            raise ValueError(msg)
        return v
