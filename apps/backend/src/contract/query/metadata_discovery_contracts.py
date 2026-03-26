"""Contract helpers for topic and geography discovery errors."""

from __future__ import annotations

from .dataset_discovery_contracts import QueryErrorEnvelope, QueryErrorPayload


def topic_not_found_error(topic_id: str) -> QueryErrorEnvelope:
    """Build a standard topic-not-found error response."""
    return QueryErrorEnvelope(
        error=QueryErrorPayload(
            code="topic_not_found",
            message=f"Topic with id '{topic_id}' was not found",
        )
    )


def geography_not_found_error(geography_id: str) -> QueryErrorEnvelope:
    """Build a standard geography-not-found error response."""
    return QueryErrorEnvelope(
        error=QueryErrorPayload(
            code="geography_not_found",
            message=f"Geography with id '{geography_id}' was not found",
        )
    )
