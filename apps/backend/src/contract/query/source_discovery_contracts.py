"""Contract helpers for source discovery errors."""

from __future__ import annotations

from .dataset_discovery_contracts import QueryErrorEnvelope, QueryErrorPayload


def source_not_found_error(source_id: str) -> QueryErrorEnvelope:
    """Build a standard source-not-found error response."""
    return QueryErrorEnvelope(
        error=QueryErrorPayload(
            code="source_not_found",
            message=f"Source with id '{source_id}' was not found",
        )
    )
