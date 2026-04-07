"""Upgrade trend descriptor persistence to v2 contract fields.

Revision ID: 0016_trend_descriptor_v2_contract
Revises: 0015_trend_notifications
Create Date: 2026-04-07
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0016_trend_descriptor_v2_contract"
down_revision: str | None = "0015_trend_notifications"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add v2 descriptor/evidence fields and widen direction domains."""

    op.drop_constraint(
        "ck_trend_lookback_snapshots_direction",
        "trend_lookback_snapshots",
        type_="check",
    )
    op.add_column(
        "trend_lookback_snapshots",
        sa.Column(
            "descriptor_state",
            sa.String(length=16),
            nullable=False,
            server_default="available",
        ),
    )
    op.add_column(
        "trend_lookback_snapshots",
        sa.Column("confidence_score", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_lookback_snapshots",
        sa.Column("dominant_measure_family", sa.String(length=16), nullable=True),
    )
    op.add_column(
        "trend_lookback_snapshots",
        sa.Column("theil_sen_slope", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_lookback_snapshots",
        sa.Column("theil_sen_low_slope", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_lookback_snapshots",
        sa.Column("theil_sen_high_slope", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_lookback_snapshots",
        sa.Column("kendall_tau", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_lookback_snapshots",
        sa.Column("kendall_pvalue", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_lookback_snapshots",
        sa.Column("ols_slope", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_lookback_snapshots",
        sa.Column("ols_intercept", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_lookback_snapshots",
        sa.Column("ols_r_squared", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_lookback_snapshots",
        sa.Column("ols_pvalue", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_lookback_snapshots",
        sa.Column("preprocessing", postgresql.JSONB(), nullable=True),
    )
    op.add_column(
        "trend_lookback_snapshots",
        sa.Column("reason_code", sa.String(length=64), nullable=True),
    )
    op.create_check_constraint(
        "ck_trend_lookback_snapshots_direction",
        "trend_lookback_snapshots",
        "direction IS NULL OR direction IN ('up', 'down', 'flat')",
    )
    op.create_check_constraint(
        "ck_trend_lookback_snapshots_descriptor_state",
        "trend_lookback_snapshots",
        "descriptor_state IN ('available', 'unavailable')",
    )
    op.create_check_constraint(
        "ck_trend_lookback_snapshots_confidence_score",
        "trend_lookback_snapshots",
        "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
    )
    op.execute(
        "ALTER TABLE trend_lookback_snapshots ALTER COLUMN descriptor_state DROP DEFAULT"
    )

    op.drop_constraint(
        "ck_trend_canonical_descriptors_direction",
        "trend_canonical_descriptors",
        type_="check",
    )
    op.add_column(
        "trend_canonical_descriptors",
        sa.Column(
            "descriptor_version",
            sa.String(length=8),
            nullable=False,
            server_default="v2",
        ),
    )
    op.add_column(
        "trend_canonical_descriptors",
        sa.Column("confidence_score", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_canonical_descriptors",
        sa.Column("dominant_measure_family", sa.String(length=16), nullable=True),
    )
    op.add_column(
        "trend_canonical_descriptors",
        sa.Column("medium_horizon_weight", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_canonical_descriptors",
        sa.Column("short_horizon_weight", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_canonical_descriptors",
        sa.Column("long_horizon_weight", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_canonical_descriptors",
        sa.Column("preprocessing", postgresql.JSONB(), nullable=True),
    )
    op.add_column(
        "trend_canonical_descriptors",
        sa.Column("ols_slope", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_canonical_descriptors",
        sa.Column("ols_intercept", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_canonical_descriptors",
        sa.Column("ols_r_squared", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_canonical_descriptors",
        sa.Column("ols_pvalue", sa.Float(), nullable=True),
    )
    op.add_column(
        "trend_canonical_descriptors",
        sa.Column("reason_code", sa.String(length=64), nullable=True),
    )
    op.create_check_constraint(
        "ck_trend_canonical_descriptors_direction",
        "trend_canonical_descriptors",
        "canonical_direction IS NULL OR canonical_direction IN ('up', 'down', 'flat')",
    )
    op.create_check_constraint(
        "ck_trend_canonical_descriptors_confidence_score",
        "trend_canonical_descriptors",
        "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
    )
    op.execute(
        "ALTER TABLE trend_canonical_descriptors ALTER COLUMN descriptor_version DROP DEFAULT"
    )


def downgrade() -> None:
    """Drop v2 descriptor/evidence fields and restore previous direction domains."""

    op.drop_constraint(
        "ck_trend_canonical_descriptors_confidence_score",
        "trend_canonical_descriptors",
        type_="check",
    )
    op.drop_constraint(
        "ck_trend_canonical_descriptors_direction",
        "trend_canonical_descriptors",
        type_="check",
    )
    op.drop_column("trend_canonical_descriptors", "reason_code")
    op.drop_column("trend_canonical_descriptors", "ols_pvalue")
    op.drop_column("trend_canonical_descriptors", "ols_r_squared")
    op.drop_column("trend_canonical_descriptors", "ols_intercept")
    op.drop_column("trend_canonical_descriptors", "ols_slope")
    op.drop_column("trend_canonical_descriptors", "preprocessing")
    op.drop_column("trend_canonical_descriptors", "long_horizon_weight")
    op.drop_column("trend_canonical_descriptors", "short_horizon_weight")
    op.drop_column("trend_canonical_descriptors", "medium_horizon_weight")
    op.drop_column("trend_canonical_descriptors", "dominant_measure_family")
    op.drop_column("trend_canonical_descriptors", "confidence_score")
    op.drop_column("trend_canonical_descriptors", "descriptor_version")
    op.create_check_constraint(
        "ck_trend_canonical_descriptors_direction",
        "trend_canonical_descriptors",
        "canonical_direction IS NULL OR canonical_direction IN ('up', 'down')",
    )

    op.drop_constraint(
        "ck_trend_lookback_snapshots_confidence_score",
        "trend_lookback_snapshots",
        type_="check",
    )
    op.drop_constraint(
        "ck_trend_lookback_snapshots_descriptor_state",
        "trend_lookback_snapshots",
        type_="check",
    )
    op.drop_constraint(
        "ck_trend_lookback_snapshots_direction",
        "trend_lookback_snapshots",
        type_="check",
    )
    op.drop_column("trend_lookback_snapshots", "reason_code")
    op.drop_column("trend_lookback_snapshots", "preprocessing")
    op.drop_column("trend_lookback_snapshots", "ols_pvalue")
    op.drop_column("trend_lookback_snapshots", "ols_r_squared")
    op.drop_column("trend_lookback_snapshots", "ols_intercept")
    op.drop_column("trend_lookback_snapshots", "ols_slope")
    op.drop_column("trend_lookback_snapshots", "kendall_pvalue")
    op.drop_column("trend_lookback_snapshots", "kendall_tau")
    op.drop_column("trend_lookback_snapshots", "theil_sen_high_slope")
    op.drop_column("trend_lookback_snapshots", "theil_sen_low_slope")
    op.drop_column("trend_lookback_snapshots", "theil_sen_slope")
    op.drop_column("trend_lookback_snapshots", "dominant_measure_family")
    op.drop_column("trend_lookback_snapshots", "confidence_score")
    op.drop_column("trend_lookback_snapshots", "descriptor_state")
    op.create_check_constraint(
        "ck_trend_lookback_snapshots_direction",
        "trend_lookback_snapshots",
        "direction IS NULL OR direction IN ('up', 'down')",
    )
