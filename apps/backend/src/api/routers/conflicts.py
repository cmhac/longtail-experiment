"""Router for GET /api/conflicts."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...repositories.conflict_repository import ConflictRepository
from ..dependencies import get_db_session
from ..schemas.common import ErrorResponse, PaginatedResponse
from ..schemas.conflicts import VALID_CONFLICT_STATES, ConflictRecordResponse

router = APIRouter()
_conflict_repo = ConflictRepository()

_UNPROCESSABLE = 422


class _ConflictQueryParams:
    """Dependency class collecting all optional conflict filter parameters."""

    def __init__(
        self,
        run_id: Annotated[str | None, Query(description="Filter by run identifier")] = None,
        source_key: Annotated[str | None, Query(description="Filter by source key")] = None,
        series_key: Annotated[str | None, Query(description="Filter by series key")] = None,
        reference_period_key: Annotated[
            str | None, Query(description="Filter by reference period key")
        ] = None,
        conflict_state: Annotated[str | None, Query(description="Filter by conflict state")] = None,
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(ge=1, le=200)] = 50,
    ) -> None:
        self.run_id = run_id or None if run_id == "" else run_id
        self.source_key = source_key or None if source_key == "" else source_key
        self.series_key = series_key or None if series_key == "" else series_key
        self.reference_period_key = (
            reference_period_key or None if reference_period_key == "" else reference_period_key
        )
        self.conflict_state = conflict_state
        self.page = page
        self.page_size = page_size


@router.get(
    "/conflicts",
    response_model=PaginatedResponse[ConflictRecordResponse],
    tags=["conflicts"],
)
def list_conflicts(
    session: Annotated[Session, Depends(get_db_session)],
    params: Annotated[_ConflictQueryParams, Depends(_ConflictQueryParams)],
) -> PaginatedResponse[ConflictRecordResponse]:
    """Return a paginated list of conflict records with optional filters."""
    if params.conflict_state is not None and (params.conflict_state not in VALID_CONFLICT_STATES):
        valid = ", ".join(sorted(VALID_CONFLICT_STATES))
        raise HTTPException(
            status_code=_UNPROCESSABLE,
            detail=ErrorResponse(
                code="validation_error",
                message=f"conflict_state must be one of: {valid}",
                details={
                    "field": "conflict_state",
                    "received": params.conflict_state,
                },
            ).model_dump(),
        )

    conflicts, total = _conflict_repo.list_conflicts(
        session,
        run_id=params.run_id,
        source_key=params.source_key,
        series_key=params.series_key,
        reference_period_key=params.reference_period_key,
        conflict_state=params.conflict_state,
        page=params.page,
        page_size=params.page_size,
    )
    return PaginatedResponse(
        items=[ConflictRecordResponse.model_validate(c) for c in conflicts],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )
