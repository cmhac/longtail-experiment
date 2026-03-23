"""SQLAlchemy read repository for source_eligibility_snapshots table."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "libs/db/src"))

from db.models.ingestion_runtime import SourceEligibilitySnapshot
from sqlalchemy import select
from sqlalchemy.orm import Session

from .base import apply_pagination


class EligibilityRepository:
    """Read-only repository for SourceEligibilitySnapshot records."""

    def list_eligibility_for_run(
        self,
        session: Session,
        run_id: str,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[SourceEligibilitySnapshot], int]:
        """List eligibility snapshots for a specific run with pagination."""
        query = select(SourceEligibilitySnapshot).where(SourceEligibilitySnapshot.run_id == run_id)
        return apply_pagination(session, query, page=page, page_size=page_size)
