"""Add dataset metadata fields and topic-tag relationships.

Revision ID: 0007_dataset_metadata_topic_tags
Revises: 0006_series_ownership_transition
Create Date: 2026-03-22
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0007_dataset_metadata_topic_tags"
down_revision: str | None = "0006_series_ownership_transition"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add dataset metadata columns and normalized topic tag tables."""
    op.add_column("data_series", sa.Column("title", sa.String(length=255), nullable=True))
    op.add_column("data_series", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "data_series", sa.Column("geographic_scope", sa.String(length=255), nullable=True)
    )

    op.execute(
        """
        UPDATE data_series
        SET title = COALESCE(title, metric_name)
        """
    )
    op.alter_column("data_series", "title", nullable=False)

    op.create_table(
        "topic_tags",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tag_name", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tag_name"),
    )

    op.create_table(
        "data_series_topic_tags",
        sa.Column("data_series_id", sa.UUID(), nullable=False),
        sa.Column("topic_tag_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["data_series_id"], ["data_series.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["topic_tag_id"], ["topic_tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("data_series_id", "topic_tag_id"),
    )
    op.create_index(
        "ix_data_series_topic_tags_topic_tag_id",
        "data_series_topic_tags",
        ["topic_tag_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove dataset metadata columns and topic-tag relationship tables."""
    op.drop_index("ix_data_series_topic_tags_topic_tag_id", table_name="data_series_topic_tags")
    op.drop_table("data_series_topic_tags")
    op.drop_table("topic_tags")
    op.drop_column("data_series", "geographic_scope")
    op.drop_column("data_series", "description")
    op.drop_column("data_series", "title")
