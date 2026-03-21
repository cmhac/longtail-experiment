"""US2 provenance repository adapter with immutable field enforcement."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProvenanceRow:
    """Immutable provenance row persisted by repository adapters."""

    observation_id: str
    release_id: str
    source_url: str


class InMemoryProvenanceRepository:
    """In-memory provenance adapter for contract tests and local flows."""

    def __init__(self) -> None:
        """Initialize empty immutable provenance store keyed by observation id."""
        self._rows: dict[str, ProvenanceRow] = {}

    def add_release(
        self, observation_id: str, release_id: str, source_url: str
    ) -> None:
        """Persist immutable provenance metadata for an observation."""
        if observation_id in self._rows:
            raise ValueError("provenance for observation is immutable once persisted")
        self._rows[observation_id] = ProvenanceRow(
            observation_id=observation_id,
            release_id=release_id,
            source_url=source_url,
        )

    def get_release(self, observation_id: str) -> ProvenanceRow | None:
        """Fetch immutable provenance metadata for one observation."""
        return self._rows.get(observation_id)
