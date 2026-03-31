"""Schema-level invariants for trend lifecycle models."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from db.models import TrendRecord, TrendTransitionEvent


def test_trend_models_have_expected_table_names() -> None:
    """Trend ORM mappings should target stable table names."""
    assert TrendRecord.__tablename__ == "trend_records"
    assert TrendTransitionEvent.__tablename__ == "trend_transition_events"


def test_trend_record_columns_include_lifecycle_fields() -> None:
    """Trend records should expose required lifecycle columns."""
    columns = TrendRecord.__table__.columns.keys()
    assert "data_series_id" in columns
    assert "trend_label" in columns
    assert "start_period" in columns
    assert "end_period" in columns
    assert "is_ongoing" in columns


def test_trend_transition_columns_include_link_fields() -> None:
    """Transition rows should link prior/new trend records when available."""
    columns = TrendTransitionEvent.__table__.columns.keys()
    assert "prior_trend_record_id" in columns
    assert "new_trend_record_id" in columns
    assert "trigger_observation_on" in columns
