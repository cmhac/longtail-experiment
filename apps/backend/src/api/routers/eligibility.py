"""Router for GET /api/runs/{run_id}/eligibility."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...repositories.eligibility_repository import EligibilityRepository
from ...repositories.run_repository import RunRepository
from ..dependencies import get_db_session
from ..schemas.common import PaginatedResponse
from ..schemas.eligibility import SourceEligibilityResponse

router = APIRouter()
_run_repo = RunRepository()
_eligibility_repo = EligibilityRepository()


@router.get(
    "/runs/{run_id}/eligibility",
    response_model=PaginatedResponse[SourceEligibilityResponse],
    tags=["eligibility"],
)
def list_eligibility(
    run_id: str,
    session: Annotated[Session, Depends(get_db_session)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 50,
) -> PaginatedResponse[SourceEligibilityResponse]:
    """Return a paginated list of eligibility snapshots for the specified run."""
    run = _run_repo.get_run_by_run_id(session, run_id)
    if run is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "not_found", "message": f"Run '{run_id}' not found"},
        )
    records, total = _eligibility_repo.list_eligibility_for_run(
        session, run_id, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=[SourceEligibilityResponse.model_validate(r) for r in records],
        total=total,
        page=page,
        page_size=page_size,
    )
