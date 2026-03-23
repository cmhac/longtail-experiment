"""SQLAlchemy read repository for ingestion_runs table."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "libs/db/src"))

from db.models.ingestion_runtime import IngestionRun
from sqlalchemy import select
from sqlalchemy.orm import Session

from .base import apply_pagination


class RunRepository:
    """Read-only repository for IngestionRun records."""

    def list_runs(
        self,
        session: Session,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[IngestionRun], int]:
        """List ingestion runs ordered by started_at descending with pagination."""
        query = select(IngestionRun).order_by(IngestionRun.started_at.desc())
        return apply_pagination(session, query, page=page, page_size=page_size)

    def get_run_by_run_id(
        self,
        session: Session,
        run_id: str,
    ) -> IngestionRun | None:
        """Return a single IngestionRun by its string run_id, or None if not found."""
        return session.scalar(select(IngestionRun).where(IngestionRun.run_id == run_id))
