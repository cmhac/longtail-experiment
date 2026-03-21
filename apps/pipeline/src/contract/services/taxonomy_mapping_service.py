"""US3 taxonomy and geography hierarchy mapping service."""

from __future__ import annotations

from src.contract.schemas.category_hierarchy import CategoryNode
from src.contract.schemas.geography_hierarchy import GeographyNode


class TaxonomyMappingService:
    """Validates hierarchy trees used for series-to-taxonomy assignments."""

    def validate_category_tree(self, nodes: list[CategoryNode]) -> dict[str, set[str]]:
        """Validate category references and return parent->children mapping."""
        by_id = {node.category_id: node for node in nodes}
        children: dict[str, set[str]] = {node.category_id: set() for node in nodes}

        for node in nodes:
            if node.parent_id is None:
                continue
            if node.parent_id not in by_id:
                raise ValueError("missing parent category for node")
            children[node.parent_id].add(node.category_id)

        return children

    def validate_geography_tree(self, nodes: list[GeographyNode]) -> dict[str, list[str]]:
        """Validate geography references and return node->ancestor lineage."""
        by_id = {node.geo_id: node for node in nodes}
        lineage: dict[str, list[str]] = {}

        def ancestors(node_id: str) -> list[str]:
            chain: list[str] = []
            current = by_id[node_id]
            seen: set[str] = {node_id}
            while current.parent_id is not None:
                parent_id = current.parent_id
                if parent_id not in by_id:
                    raise ValueError("missing parent geography for node")
                if parent_id in seen:
                    raise ValueError("geography cycle detected")
                chain.insert(0, parent_id)
                seen.add(parent_id)
                current = by_id[parent_id]
            return chain

        for node in nodes:
            lineage[node.geo_id] = ancestors(node.geo_id)

        return lineage
