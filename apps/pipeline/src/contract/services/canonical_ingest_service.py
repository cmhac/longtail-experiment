"""Canonical ingest service for US1 contract flow."""

from __future__ import annotations

from typing import Any

from src.contract.errors import ContractValidationError
from src.contract.normalizers.source_payload_mapper import normalize_source_payload
from src.contract.schemas.canonical_observation import CanonicalObservation


class CanonicalIngestService:
    """Validates and writes normalized observations through repository boundaries."""

    def __init__(self, repository: Any) -> None:
        """Initialize service with the repository used for persistence."""
        self._repository = repository

    def ingest_payload(self, payload: dict[str, object]) -> CanonicalObservation:
        """Normalize, validate, and persist a source payload."""
        try:
            observation = normalize_source_payload(payload)
        except Exception as exc:  # pragma: no cover - explicit conversion boundary
            raise ContractValidationError(str(exc)) from exc

        if hasattr(self._repository, "upsert_observation"):
            self._repository.upsert_observation(observation)
        else:
            self._repository.upsert_value(
                observation.series_key,
                observation.observed_on,
                observation.value,
            )

        return observation
