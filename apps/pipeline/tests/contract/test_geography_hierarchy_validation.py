"""Tests for geography hierarchy and non-geographic handling."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.schemas.geography_hierarchy import GeographyNode
from src.contract.services.taxonomy_mapping_service import TaxonomyMappingService


def test_geography_tree_allows_multilevel_assignment() -> None:
    """Series can be assigned at deep geography levels while preserving ancestry."""
    service = TaxonomyMappingService()
    world = GeographyNode(geo_id="world", parent_id=None, kind="region")
    usa = GeographyNode(geo_id="usa", parent_id="world", kind="country")
    ca = GeographyNode(geo_id="ca", parent_id="usa", kind="state")

    lineage = service.validate_geography_tree([world, usa, ca])

    assert lineage["ca"] == ["world", "usa"]


def test_geography_tree_allows_non_geographic_marker() -> None:
    """Non-geographic series should be explicitly tagged and queryable."""
    marker = GeographyNode.non_geographic_marker()

    assert marker.geo_id == "__non_geographic__"
    assert marker.kind == "non_geographic"


def test_geography_tree_rejects_unknown_kind() -> None:
    """Only known geography kinds should be accepted."""
    with pytest.raises(ValueError, match="invalid geography kind"):
        GeographyNode(geo_id="x", parent_id=None, kind="planet")
