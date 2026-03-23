"""FastAPI application factory for the longtail backend API."""

from __future__ import annotations

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .routers import conflicts, eligibility, health, outcomes, runs
from .schemas.common import ErrorResponse

logger = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Longtail Backend API",
        description="Read-only API for ingested data",
        version="1.0.0",
    )

    # Register exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Return a structured ErrorResponse envelope for all HTTP exceptions."""
        detail = exc.detail
        if isinstance(detail, dict) and "code" in detail:
            body = detail
        else:
            body = ErrorResponse(
                code="error",
                message=str(detail),
            ).model_dump()
        return JSONResponse(status_code=exc.status_code, content=body)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Return a structured ErrorResponse envelope for validation errors."""
        body = ErrorResponse(
            code="validation_error",
            message="Request validation failed",
            details={"errors": exc.errors()},
        ).model_dump()
        return JSONResponse(status_code=422, content=body)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Return a 503 envelope for unexpected errors without exposing internals."""
        logger.exception("Unhandled exception", exc_info=exc)
        body = ErrorResponse(
            code="service_unavailable",
            message="An unexpected error occurred",
        ).model_dump()
        return JSONResponse(status_code=503, content=body)

    # Register routers
    app.include_router(health.router)
    app.include_router(runs.router, prefix="/api")
    app.include_router(outcomes.router, prefix="/api")
    app.include_router(eligibility.router, prefix="/api")
    app.include_router(conflicts.router, prefix="/api")

    return app
