"""Shared contract helpers for dataset discovery query responses."""

from __future__ import annotations

from pydantic import BaseModel, Field


class QueryErrorPayload(BaseModel):
    """Error payload returned by contract query workflows."""

    code: str = Field(min_length=1)
    message: str = Field(min_length=1)


class QueryErrorEnvelope(BaseModel):
    """Envelope used for standardized query errors."""

    error: QueryErrorPayload


def invalid_request_error(message: str) -> QueryErrorEnvelope:
    """Build a standard invalid-request error response."""
    return QueryErrorEnvelope(
        error=QueryErrorPayload(
            code="invalid_request",
            message=message,
        )
    )


def dataset_not_found_error(dataset_id: str) -> QueryErrorEnvelope:
    """Build a standard dataset-not-found error response."""
    return QueryErrorEnvelope(
        error=QueryErrorPayload(
            code="dataset_not_found",
            message=f"Dataset with id '{dataset_id}' was not found",
        )
    )
