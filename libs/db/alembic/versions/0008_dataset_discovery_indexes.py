"""Add dataset discovery read indexes.

Revision ID: 0008_dataset_discovery_indexes
Revises: 0007_dataset_metadata_topic_tags
Create Date: 2026-03-23
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0008_dataset_discovery_indexes"
down_revision: str | None = "0007_dataset_metadata_topic_tags"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add indexes used by dataset discovery search and recency reads."""

    op.create_index(
        "ix_data_series_title_lower",
        "data_series",
        [op.f("title")],
        unique=False,
        postgresql_ops={"title": "text_pattern_ops"},
    )
    op.create_index(
        "ix_data_series_source_profile_id_title",
        "data_series",
        ["source_profile_id", "title"],
        unique=False,
    )
    op.create_index(
        "ix_observations_series_id_reported_at",
        "observations",
        ["series_id", "reported_at"],
        unique=False,
    )
    op.create_index(
        "ix_observations_series_id_observed_on",
        "observations",
        ["series_id", "observed_on"],
        unique=False,
    )


def downgrade() -> None:
    """Remove indexes used by dataset discovery reads."""

    op.drop_index("ix_observations_series_id_observed_on", table_name="observations")
    op.drop_index("ix_observations_series_id_reported_at", table_name="observations")
    op.drop_index("ix_data_series_source_profile_id_title", table_name="data_series")
    op.drop_index("ix_data_series_title_lower", table_name="data_series")
