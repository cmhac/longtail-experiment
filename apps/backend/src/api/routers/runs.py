"""Routers for GET /api/runs and GET /api/runs/{run_id}."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...repositories.run_repository import RunRepository
from ..dependencies import get_db_session
from ..schemas.common import PaginatedResponse
from ..schemas.runs import IngestionRunResponse

router = APIRouter()
_repo = RunRepository()


@router.get(
    "/runs",
    response_model=PaginatedResponse[IngestionRunResponse],
    tags=["runs"],
)
def list_runs(
    session: Annotated[Session, Depends(get_db_session)],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    page_size: Annotated[int, Query(ge=1, le=200, description="Items per page (1-200)")] = 50,
) -> PaginatedResponse[IngestionRunResponse]:
    """Return a paginated list of ingestion runs ordered by started_at descending."""
    runs, total = _repo.list_runs(session, page=page, page_size=page_size)
    return PaginatedResponse(
        items=[IngestionRunResponse.model_validate(r) for r in runs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/runs/{run_id}",
    response_model=IngestionRunResponse,
    tags=["runs"],
)
def get_run(
    run_id: str,
    session: Annotated[Session, Depends(get_db_session)],
) -> IngestionRunResponse:
    """Return the full detail record for a single ingestion run."""
    run = _repo.get_run_by_run_id(session, run_id)
    if run is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "not_found", "message": f"Run '{run_id}' not found"},
        )
    return IngestionRunResponse.model_validate(run)
