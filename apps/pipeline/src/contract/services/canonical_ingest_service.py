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

    def sync_source_metadata(
        self,
        *,
        source_key: str,
        source_name: str,
        source_title: str,
        source_description: str,
        source_type: str,
    ) -> None:
        """Persist source metadata independently of observation writes."""
        if hasattr(self._repository, "upsert_source_profile"):
            self._repository.upsert_source_profile(
                source_key=source_key,
                source_name=source_name,
                source_title=source_title,
                source_description=source_description,
                source_type=source_type,
            )
