"""Tests for taxonomy hierarchy validation behavior."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.schemas.category_hierarchy import CategoryNode
from src.contract.services.taxonomy_mapping_service import TaxonomyMappingService


def test_category_node_accepts_valid_parent_child_relationships() -> None:
    """Valid parent/child references should be accepted for mapping workflows."""
    root = CategoryNode(category_id="economy", parent_id=None, label="Economy")
    child = CategoryNode(category_id="labor", parent_id="economy", label="Labor")

    service = TaxonomyMappingService()
    mapping = service.validate_category_tree([root, child])

    assert mapping["economy"] == {"labor"}


def test_category_node_rejects_self_parent_cycles() -> None:
    """A category cannot be its own parent."""
    service = TaxonomyMappingService()

    with pytest.raises(ValueError, match="cannot reference itself as parent"):
        service.validate_category_tree(
            [
                CategoryNode(
                    category_id="economy",
                    parent_id="economy",
                    label="Economy",
                )
            ]
        )


def test_category_node_rejects_missing_parent_references() -> None:
    """All non-root categories must reference an existing parent category."""
    service = TaxonomyMappingService()

    with pytest.raises(ValueError, match="missing parent"):
        service.validate_category_tree(
            [
                CategoryNode(
                    category_id="labor",
                    parent_id="economy",
                    label="Labor",
                )
            ]
        )
