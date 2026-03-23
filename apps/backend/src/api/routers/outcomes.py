"""Router for GET /api/runs/{run_id}/outcomes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...repositories.outcome_repository import OutcomeRepository
from ...repositories.run_repository import RunRepository
from ..dependencies import get_db_session
from ..schemas.common import ErrorResponse, PaginatedResponse
from ..schemas.outcomes import SourceRunOutcomeResponse

router = APIRouter()
_run_repo = RunRepository()
_outcome_repo = OutcomeRepository()

_NOT_FOUND = 404


@router.get(
    "/runs/{run_id}/outcomes",
    response_model=PaginatedResponse[SourceRunOutcomeResponse],
    tags=["outcomes"],
)
def list_outcomes(
    run_id: str,
    session: Annotated[Session, Depends(get_db_session)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 50,
) -> PaginatedResponse[SourceRunOutcomeResponse]:
    """Return a paginated list of source run outcomes for the specified run."""
    run = _run_repo.get_run_by_run_id(session, run_id)
    if run is None:
        raise HTTPException(
            status_code=_NOT_FOUND,
            detail=ErrorResponse(
                code="not_found",
                message=f"Run '{run_id}' not found",
            ).model_dump(),
        )
    outcomes, total = _outcome_repo.list_outcomes_for_run(
        session, run_id, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=[SourceRunOutcomeResponse.model_validate(o) for o in outcomes],
        total=total,
        page=page,
        page_size=page_size,
    )
