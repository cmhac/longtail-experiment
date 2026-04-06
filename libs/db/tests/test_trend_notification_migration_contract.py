"""Contract tests for trend notification migration and ORM schema surface."""

from __future__ import annotations

import importlib
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import cast

from sqlalchemy import CheckConstraint, Table, UniqueConstraint

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

models = importlib.import_module("db.models")
TrendChangeEvent = models.TrendChangeEvent
UserDatasetSubscription = models.UserDatasetSubscription
UserTrendNotification = models.UserTrendNotification


def test_trend_notification_migration_metadata() -> None:
    """Migration 0015 should chain from owner-privilege governance."""

    file_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0015_trend_notifications.py"
    )
    spec = spec_from_file_location("trend_notifications", file_path)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.revision == "0015_trend_notifications"
    assert module.down_revision == "0014_owner_privilege_governance"


def test_notification_models_expose_expected_tables_and_columns() -> None:
    """Notification ORM models should expose stable table names and key columns."""

    expected_contract = (
        (
            TrendChangeEvent,
            "trend_change_events",
            {
                "data_series_id",
                "previous_direction",
                "current_direction",
                "effective_observed_on",
                "processing_context",
                "visibility_classification",
                "idempotency_fingerprint",
                "emitted_at",
            },
        ),
        (
            UserDatasetSubscription,
            "user_dataset_subscriptions",
            {
                "user_id",
                "data_series_id",
                "subscribed_at",
                "updated_at",
            },
        ),
        (
            UserTrendNotification,
            "user_trend_notifications",
            {
                "event_id",
                "user_id",
                "data_series_id",
                "destination_path",
                "title",
                "body",
                "unread_state",
                "delivered_at",
                "channel",
                "delivery_status",
            },
        ),
    )

    for model, expected_table_name, required_columns in expected_contract:
        table = model.__table__
        assert model.__tablename__ == expected_table_name
        for column_name in required_columns:
            assert column_name in table.columns
            assert table.columns[column_name].nullable is False


def test_notification_constraints_and_indexes_match_expected_names() -> None:
    """Constraint/index names should match migration and ORM contract names."""

    migration_text = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0015_trend_notifications.py"
    ).read_text(encoding="utf-8")

    expected_names_by_table = (
        (
            TrendChangeEvent.__table__,
            {
                "uq_trend_change_events_idempotency_fingerprint",
            },
            {
                "ck_trend_change_events_previous_direction",
                "ck_trend_change_events_current_direction",
                "ck_trend_change_events_processing_context",
                "ck_trend_change_events_visibility_classification",
            },
            {
                "ix_trend_change_events_series_observed_on",
            },
        ),
        (
            UserDatasetSubscription.__table__,
            set(),
            set(),
            {
                "ix_user_dataset_subscriptions_user_active",
                "ix_user_dataset_subscriptions_series_active",
            },
        ),
        (
            UserTrendNotification.__table__,
            {
                "uq_user_trend_notifications_event_user",
            },
            {
                "ck_user_trend_notifications_unread_state",
                "ck_user_trend_notifications_channel",
                "ck_user_trend_notifications_delivery_status",
                "ck_user_trend_notifications_read_state",
            },
            {
                "ix_user_trend_notifications_user_delivery",
                "ix_user_trend_notifications_user_unread",
            },
        ),
    )

    for (
        table,
        expected_unique,
        expected_check,
        expected_indexes,
    ) in expected_names_by_table:
        typed_table = cast(Table, table)
        unique_names = {
            constraint.name
            for constraint in typed_table.constraints
            if isinstance(constraint, UniqueConstraint) and constraint.name
        }
        check_names = {
            constraint.name
            for constraint in typed_table.constraints
            if isinstance(constraint, CheckConstraint) and constraint.name
        }
        index_names = {index.name for index in typed_table.indexes if index.name}

        assert unique_names == expected_unique
        assert check_names == expected_check
        assert index_names == expected_indexes

        for expected_name in expected_unique | expected_check | expected_indexes:
            assert expected_name in migration_text

    assert "uq_user_dataset_subscriptions_user_series_active" in migration_text
