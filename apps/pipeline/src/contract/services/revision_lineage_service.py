"""US2 lineage service for revision event validation and linking."""

from __future__ import annotations

from datetime import date

from src.contract.schemas.revision_record import RevisionRecord


class RevisionLineageService:
    """Validate and build revision lineage records."""

    @staticmethod
    def _as_date(value: object) -> date:
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value))

    def link_revision(
        self,
        *,
        superseded: dict[str, object],
        current: dict[str, object],
        revision_reason: str,
    ) -> RevisionRecord:
        """Create a revision link while enforcing series and period compatibility."""
        superseded_series = str(superseded["series_key"])
        current_series = str(current["series_key"])
        if superseded_series != current_series:
            raise ValueError("revision links require matching series keys")

        superseded_start = superseded["reference_period_start"]
        current_start = current["reference_period_start"]
        superseded_end = superseded["reference_period_end"]
        current_end = current["reference_period_end"]
        if superseded_start != current_start or superseded_end != current_end:
            raise ValueError("revision links require matching reference period boundaries")

        return RevisionRecord(
            superseded_observation_id=str(superseded["observation_id"]),
            current_observation_id=str(current["observation_id"]),
            revision_reason=revision_reason,
            series_key=superseded_series,
            reference_period_start=self._as_date(superseded_start),
            reference_period_end=self._as_date(superseded_end),
        )
