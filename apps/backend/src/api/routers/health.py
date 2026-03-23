"""GET /health router — service liveness and DB reachability check."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "libs/db/src"))

from db import create_db_engine, resolve_database_url
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from ..schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def get_health() -> HealthResponse | JSONResponse:
    """Check service health and database reachability."""
    url = resolve_database_url(explicit_url=None)
    engine = create_db_engine(url)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "reachable"
    except OperationalError:
        db_status = "unreachable"
        engine.dispose()
        return JSONResponse(
            status_code=503,
            content={
                "code": "service_unavailable",
                "message": "Database is unreachable",
                "details": {"db": "unreachable"},
            },
        )
    finally:
        engine.dispose()

    return HealthResponse(status="ok", db=db_status)
