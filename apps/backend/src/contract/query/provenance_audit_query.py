"""US2 backend provenance and revision audit query service."""

from __future__ import annotations

from typing import Any

from src.contract.errors import ContractQueryError


class ProvenanceAuditQueryService:
    """Read provenance and revision history rows for audit workflows."""

    def __init__(self, repository: Any) -> None:
        """Initialize query service with a repository dependency."""
        self._repository = repository

    def fetch_audit_history(self, series_key: str) -> list[dict[str, object]]:
        """Return provenance and revision rows for the provided series key."""
        if not hasattr(self._repository, "fetch_provenance_and_revisions"):
            raise ContractQueryError("Repository does not provide fetch_provenance_and_revisions")
        rows = self._repository.fetch_provenance_and_revisions(series_key)
        if not isinstance(rows, list):
            raise ContractQueryError("Audit repository response must be a list")
        return rows
