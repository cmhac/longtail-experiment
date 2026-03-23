# Research: Initial Read-Only FastAPI API For Ingested Data

## Decision 1: Use FastAPI 0.115.x with uvicorn[standard] as the ASGI server

- Decision: Add `fastapi>=0.115.0` and `uvicorn[standard]>=0.32.0` to `apps/backend` dependencies. Use synchronous SQLAlchemy sessions (not async) via the existing `libs/db` engine/session utilities.
- Rationale: FastAPI 0.115.x is stable, Pydantic 2.x-native, and already the implied choice given the existing Pydantic 2.x dependency. Synchronous SQLAlchemy is appropriate here because all existing `libs/db` patterns are synchronous, the runtime tables are low-volume for Phase 1, and avoiding async avoids introducing a parallel session-management pattern.
- Alternatives considered:
  - FastAPI with async SQLAlchemy (asyncpg driver).
    - Rejected because libs/db uses synchronous psycopg 3.x sessions; introducing a second async session path would create conflicting session patterns and require new engine/session factories.
  - Starlette directly without FastAPI.
    - Rejected because FastAPI provides automatic Pydantic validation, OpenAPI generation, and dependency injection that are required by FR-007 through FR-017.

## Decision 2: Per-request DB session via FastAPI dependency injection

- Decision: Create a `get_db_session` dependency using `contextmanager`/`yield` pattern that opens a `Session` from the existing `libs/db` session factory and closes it after the request completes. The session factory is initialized at application startup using `resolve_database_url()` and `create_db_engine()` from `libs/db`.
- Rationale: Per-request sessions are safe for read-only workloads, align with SQLAlchemy best practices, and keep the session lifecycle explicit. Using the existing `libs/db` utilities avoids duplicating engine/session configuration.
- Alternatives considered:
  - Global singleton session.
    - Rejected because it is not thread-safe under multiple concurrent requests in uvicorn.
  - Middleware-based session management.
    - Rejected because FastAPI dependency injection is more testable and composable.

## Decision 3: Page-number pagination for Phase 1 list endpoints

- Decision: All list endpoints accept `page` (default 1, min 1) and `page_size` (default 50, max 200) query parameters and return a response envelope `{ "items": [...], "total": int, "page": int, "page_size": int }`.
- Rationale: Page-number pagination is simpler to implement, easier for frontend clients to consume, and sufficient for Phase 1 data volumes. Cursor-based pagination may be introduced in Phase 2 for large observation sets.
- Alternatives considered:
  - Cursor-based pagination.
    - Rejected for Phase 1 because the runtime tables have low cardinality in local development and cursor pagination adds complexity without benefit at this scale.
  - No pagination (return all rows).
    - Rejected because FR-007 requires pagination support and the spec calls for pagination-friendly design.

## Decision 4: httpx AsyncClient / TestClient for router tests; pytest fixtures for repository tests

- Decision: Use FastAPI's `TestClient` (backed by httpx) for all router/integration tests. Repository tests use in-process SQLite or mock sessions with in-memory factories to avoid requiring a live database in CI. Integration tests that require a live database are marked with a `@pytest.mark.integration` marker and skipped by default in CI.
- Rationale: `TestClient` exercises the full request/response stack including FastAPI validation, dependency injection, and serialization. Repository-level tests can use lightweight in-memory mocks consistent with the existing pattern in `apps/backend/tests/contract/`.
- Alternatives considered:
  - pytest-asyncio with async httpx client.
    - Rejected because using sync `TestClient` matches the synchronous SQLAlchemy session model and avoids introducing async test infrastructure.
  - Full database integration tests for all test cases.
    - Rejected because requiring a live Postgres instance in every test slows CI and conflicts with the existing pattern of using in-process mock repositories.

## Decision 5: Centralized exception handlers for structured 404/422/503 error envelopes

- Decision: Register FastAPI exception handlers for `HTTPException` and `RequestValidationError` to return a consistent JSON error envelope `{ "code": str, "message": str, "details": dict | null, "correlation_id": str | null }`. DB unavailability is caught in the health endpoint and returns 503.
- Rationale: FR-011 through FR-013 and FR-017 require a consistent error envelope. FastAPI's built-in `HTTPException` handler returns a different default shape; overriding it ensures all error responses are uniform.
- Alternatives considered:
  - Per-endpoint try/except blocks.
    - Rejected because it requires duplication across all routes and risks inconsistency.
  - Middleware-based error wrapping.
    - Rejected because exception handlers are the idiomatic FastAPI approach and are more composable.

## Decision 6: Checked-in OpenAPI snapshot with a test assertion for consistency

- Decision: Generate the OpenAPI JSON schema from the running FastAPI app and check it in at `specs/contracts/openapi-phase1-snapshot.json`. A test in `apps/backend/tests/api/` uses `TestClient` to fetch `/openapi.json` and compares it against the snapshot, failing if they diverge.
- Rationale: FR-015 requires a checked-in OpenAPI snapshot and SC-004 requires a consistency test. This approach is zero-dependency (no external tools) and runs in the existing pytest suite.
- Alternatives considered:
  - Generate snapshot in CI only (not checked in).
    - Rejected because the snapshot serves as the shared frontend/backend contract boundary and must be reviewable in PRs.
  - Use a third-party schema registry.
    - Rejected because it introduces an external dependency not present in the current stack.

## Decision 7: Update docker-compose.yml backend service to run FastAPI via uvicorn

- Decision: Replace the placeholder `python -m http.server 8080` command in the `backend` service with a uvicorn command that mounts the repository workspace, installs backend dependencies, and starts the FastAPI app. The healthcheck is updated to hit `GET /health`.
- Rationale: Constitution Principle IV requires local-first runtime parity; the backend service must be runnable in Docker Compose. The existing placeholder is not functional for Phase 1 endpoints.
- Alternatives considered:
  - Build a Docker image for the backend service.
    - Deferred because the current stack uses live-mounted workspace volumes for fast developer iteration (consistent with dagit service pattern).
  - Keep placeholder and document manual start only.
    - Rejected because it violates local-stack parity requirements.
