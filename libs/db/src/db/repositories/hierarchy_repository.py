"""US3 hierarchy repository adapter for descendant filter expansion."""

from __future__ import annotations


class InMemoryHierarchyRepository:
    """In-memory hierarchy repository used by backend query services."""

    def __init__(self) -> None:
        self._descendants: dict[str, list[str]] = {}

    def register_descendants(self, parent_id: str, descendants: list[str]) -> None:
        """Register a deterministic descendant list for a parent node."""
        self._descendants[parent_id] = list(descendants)

    def get_descendant_ids(self, node_id: str) -> list[str]:
        """Return descendants for a taxonomy or geography node."""
        return list(self._descendants.get(node_id, []))
