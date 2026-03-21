"""Tests for hierarchy-aware backend query filters."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.query.hierarchy_query import HierarchyQueryService


@dataclass(slots=True)
class _RepoStub:
    """Simple hierarchy repository stub for query service tests."""

    descendants: dict[str, list[str]]

    def get_descendant_ids(self, node_id: str) -> list[str]:
        """Return descendants for a category or geography node."""
        return self.descendants.get(node_id, [])


def test_parent_category_filter_expands_to_descendants() -> None:
    """Parent filters should include all descendant category ids."""
    repo = _RepoStub(descendants={"economy": ["labor", "inflation"]})
    service = HierarchyQueryService(hierarchy_repository=repo)

    resolved = service.expand_category_filter("economy")

    assert resolved == ["economy", "labor", "inflation"]


def test_parent_geography_filter_expands_to_descendants() -> None:
    """Parent geography filters should include all child geography ids."""
    repo = _RepoStub(descendants={"usa": ["ca", "ny"]})
    service = HierarchyQueryService(hierarchy_repository=repo)

    resolved = service.expand_geography_filter("usa")

    assert resolved == ["usa", "ca", "ny"]


def test_non_geographic_filter_resolves_without_descendants() -> None:
    """Non-geographic marker should resolve as a standalone filter value."""
    repo = _RepoStub(descendants={})
    service = HierarchyQueryService(hierarchy_repository=repo)

    resolved = service.expand_geography_filter("__non_geographic__")

    assert resolved == ["__non_geographic__"]
