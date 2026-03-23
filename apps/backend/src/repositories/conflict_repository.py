"""SQLAlchemy read repository for conflict_records table."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "libs/db/src"))

from db.models.ingestion_runtime import ConflictRecord  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from .base import apply_pagination  # noqa: E402

VALID_CONFLICT_STATES = frozenset({"open", "resolved", "suppressed"})

_DEFAULT_PAGE = 1
_DEFAULT_PAGE_SIZE = 50


class ConflictRepository:
    """Read-only repository for ConflictRecord records."""

    def list_conflicts(
        self,
        session: Session,
        *,
        run_id: str | None = None,
        source_key: str | None = None,
        series_key: str | None = None,
        reference_period_key: str | None = None,
        conflict_state: str | None = None,
        page: int = _DEFAULT_PAGE,
        page_size: int = _DEFAULT_PAGE_SIZE,
    ) -> tuple[list[ConflictRecord], int]:
        """List conflict records with optional filters and pagination."""
        if conflict_state is not None and conflict_state not in VALID_CONFLICT_STATES:
            msg = f"conflict_state must be one of {sorted(VALID_CONFLICT_STATES)}"
            raise ValueError(msg)

        query = select(ConflictRecord)

        if run_id is not None:
            query = query.where(ConflictRecord.run_id == run_id)
        if source_key is not None:
            query = query.where(ConflictRecord.source_key == source_key)
        if series_key is not None:
            query = query.where(ConflictRecord.series_key == series_key)
        if reference_period_key is not None:
            query = query.where(ConflictRecord.reference_period_key == reference_period_key)
        if conflict_state is not None:
            query = query.where(ConflictRecord.conflict_state == conflict_state)

        return apply_pagination(session, query, page=page, page_size=page_size)
