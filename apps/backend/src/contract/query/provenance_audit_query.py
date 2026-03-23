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

        conflict_ids: list[str] = []
        if hasattr(self._repository, "fetch_conflict_ids_for_series"):
            fetched = self._repository.fetch_conflict_ids_for_series(series_key)
            if not isinstance(fetched, list):
                raise ContractQueryError("Conflict identifiers response must be a list")
            conflict_ids = [str(item) for item in fetched]

        visibility_projection: dict[str, object] = {}
        if hasattr(self._repository, "fetch_run_visibility_for_series"):
            projection = self._repository.fetch_run_visibility_for_series(series_key)
            if not isinstance(projection, dict):
                raise ContractQueryError("Run visibility projection must be a dictionary")
            visibility_projection = {
                "due_source_count": int(projection.get("due_source_count", 0)),
                "executed_source_count": int(projection.get("executed_source_count", 0)),
                "deferred_source_count": int(projection.get("deferred_source_count", 0)),
                "not_due_source_count": int(projection.get("not_due_source_count", 0)),
                "source_visibility_reasons": list(projection.get("source_visibility_reasons", [])),
            }

        return [
            {
                **row,
                "conflict_ids": list(conflict_ids),
                **visibility_projection,
            }
            for row in rows
        ]
