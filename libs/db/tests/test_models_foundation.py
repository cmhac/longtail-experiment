"""Foundational tests for shared ORM models."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from db.models import (
    Base,
    CategoryNode,
    DataSeries,
    GeographyNode,
    Observation,
    ProvenanceRecord,
    RevisionRecord,
    DataSeriesTopicTag,
    SourceProfile,
    TopicTag,
)


def test_model_exports_available() -> None:
    assert Base is not None
    assert SourceProfile.__tablename__ == "source_profiles"
    assert DataSeries.__tablename__ == "data_series"
    assert Observation.__tablename__ == "observations"
    assert ProvenanceRecord.__tablename__ == "provenance_records"
    assert RevisionRecord.__tablename__ == "revision_records"
    assert CategoryNode.__tablename__ == "category_nodes"
    assert GeographyNode.__tablename__ == "geography_nodes"
    assert TopicTag.__tablename__ == "topic_tags"
    assert DataSeriesTopicTag.__tablename__ == "data_series_topic_tags"


def test_source_profile_model_exposes_stable_identity_and_metadata_columns() -> None:
    table = SourceProfile.__table__

    assert "source_key" in table.columns
    assert table.columns["source_key"].nullable is False
    assert table.columns["source_key"].unique is True
    assert "title" in table.columns
    assert table.columns["title"].nullable is False
    assert "description" in table.columns
    assert table.columns["description"].nullable is False
