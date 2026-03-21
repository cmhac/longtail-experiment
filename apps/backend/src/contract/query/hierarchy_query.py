"""US3 backend hierarchy-aware query filter expansion service."""

from __future__ import annotations

from typing import Any

from src.contract.errors import ContractQueryError


class HierarchyQueryService:
    """Expands parent-level hierarchy filters to include descendants."""

    def __init__(self, hierarchy_repository: Any) -> None:
        """Initialize service with repository used for descendant lookups."""
        self._repository = hierarchy_repository

    def _expand(self, node_id: str) -> list[str]:
        if not hasattr(self._repository, "get_descendant_ids"):
            raise ContractQueryError("Repository does not provide get_descendant_ids")

        descendants = self._repository.get_descendant_ids(node_id)
        if not isinstance(descendants, list):
            raise ContractQueryError("Hierarchy repository returned invalid descendants")

        return [node_id, *descendants]

    def expand_category_filter(self, category_id: str) -> list[str]:
        """Expand a parent category filter into category plus descendants."""
        return self._expand(category_id)

    def expand_geography_filter(self, geography_id: str) -> list[str]:
        """Expand a parent geography filter into geography plus descendants."""
        return self._expand(geography_id)
