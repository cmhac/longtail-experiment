"""Add trend-change events, subscriptions, and in-app notifications.

Revision ID: 0015_trend_notifications
Revises: 0014_owner_privilege_governance
Create Date: 2026-04-05
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0015_trend_notifications"
down_revision: str | None = "0014_owner_privilege_governance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create trend-notification domain tables and indexes."""

    op.create_table(
        "trend_change_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_series_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("previous_direction", sa.String(length=16), nullable=False),
        sa.Column("current_direction", sa.String(length=16), nullable=False),
        sa.Column("effective_observed_on", sa.Date(), nullable=False),
        sa.Column("processing_context", sa.String(length=32), nullable=False),
        sa.Column("visibility_classification", sa.String(length=16), nullable=False),
        sa.Column("idempotency_fingerprint", sa.String(length=255), nullable=False),
        sa.Column("emitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["data_series_id"], ["data_series.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "idempotency_fingerprint",
            name="uq_trend_change_events_idempotency_fingerprint",
        ),
        sa.CheckConstraint(
            "previous_direction IN ('up', 'down')",
            name="ck_trend_change_events_previous_direction",
        ),
        sa.CheckConstraint(
            "current_direction IN ('up', 'down')",
            name="ck_trend_change_events_current_direction",
        ),
        sa.CheckConstraint(
            "processing_context IN ('incremental', 'historical_reprocessing')",
            name="ck_trend_change_events_processing_context",
        ),
        sa.CheckConstraint(
            "visibility_classification IN ('user_visible', 'audit_only')",
            name="ck_trend_change_events_visibility_classification",
        ),
    )
    op.create_index(
        "ix_trend_change_events_series_observed_on",
        "trend_change_events",
        ["data_series_id", "effective_observed_on"],
        unique=False,
    )

    op.create_table(
        "user_dataset_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_series_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subscribed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("unsubscribed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["data_series_id"], ["data_series.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_dataset_subscriptions_user_active",
        "user_dataset_subscriptions",
        ["user_id", "unsubscribed_at"],
        unique=False,
    )
    op.create_index(
        "ix_user_dataset_subscriptions_series_active",
        "user_dataset_subscriptions",
        ["data_series_id", "unsubscribed_at"],
        unique=False,
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_user_dataset_subscriptions_user_series_active
        ON user_dataset_subscriptions (user_id, data_series_id)
        WHERE unsubscribed_at IS NULL
        """
    )

    op.create_table(
        "user_trend_notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_series_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("destination_path", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("unread_state", sa.String(length=16), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("channel", sa.String(length=16), nullable=False),
        sa.Column("delivery_status", sa.String(length=16), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_id"], ["trend_change_events.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["data_series_id"], ["data_series.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "event_id",
            "user_id",
            name="uq_user_trend_notifications_event_user",
        ),
        sa.CheckConstraint(
            "unread_state IN ('unread', 'read')",
            name="ck_user_trend_notifications_unread_state",
        ),
        sa.CheckConstraint(
            "channel IN ('in_app')",
            name="ck_user_trend_notifications_channel",
        ),
        sa.CheckConstraint(
            "delivery_status IN ('queued', 'delivered', 'failed', 'suppressed')",
            name="ck_user_trend_notifications_delivery_status",
        ),
        sa.CheckConstraint(
            "(unread_state = 'unread' AND read_at IS NULL) OR "
            "(unread_state = 'read' AND read_at IS NOT NULL)",
            name="ck_user_trend_notifications_read_state",
        ),
    )
    op.create_index(
        "ix_user_trend_notifications_user_delivery",
        "user_trend_notifications",
        ["user_id", "delivered_at", "id"],
        unique=False,
    )
    op.create_index(
        "ix_user_trend_notifications_user_unread",
        "user_trend_notifications",
        ["user_id", "unread_state"],
        unique=False,
    )


def downgrade() -> None:
    """Drop trend-notification domain tables and indexes."""

    op.drop_index(
        "ix_user_trend_notifications_user_unread",
        table_name="user_trend_notifications",
    )
    op.drop_index(
        "ix_user_trend_notifications_user_delivery",
        table_name="user_trend_notifications",
    )
    op.drop_table("user_trend_notifications")

    op.drop_index("uq_user_dataset_subscriptions_user_series_active")
    op.drop_index(
        "ix_user_dataset_subscriptions_series_active",
        table_name="user_dataset_subscriptions",
    )
    op.drop_index(
        "ix_user_dataset_subscriptions_user_active",
        table_name="user_dataset_subscriptions",
    )
    op.drop_table("user_dataset_subscriptions")

    op.drop_index(
        "ix_trend_change_events_series_observed_on",
        table_name="trend_change_events",
    )
    op.drop_table("trend_change_events")
