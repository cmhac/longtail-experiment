# Quickstart: Initial Read-Only FastAPI API For Ingested Data

## Objective

Validate that all Phase 1 read-only API endpoints start, respond, and return correct data from the local PostgreSQL runtime store.

## Prerequisites

- Repository dependencies installed:
  ```bash
  uv sync --project apps/backend --frozen
  ```
- Local Postgres running (via Docker Compose):
  ```bash
  docker compose up -d db
  docker compose ps
  ```
- Database migrations applied:
  ```bash
  bash tools/quality/local-stack/run-db-migrations.sh
  ```

## 1) Start the backend API locally

```bash
uv run --project apps/backend uvicorn src.api.app:app --host 0.0.0.0 --port 8080 --reload
```

Expected: Server starts and logs `Application startup complete.`

## 2) Verify the health endpoint

```bash
curl -s http://localhost:8080/health | python -m json.tool
```

Expected:
```json
{
  "status": "ok",
  "db": "reachable"
}
```

## 3) Verify run listing

```bash
curl -s "http://localhost:8080/api/runs?page=1&page_size=10" | python -m json.tool
```

Expected: HTTP 200 with `{ "items": [...], "total": N, "page": 1, "page_size": 10 }`. If no ingestion runs have been executed, `items` will be `[]` and `total` will be `0`.

## 4) Verify conflict listing

```bash
curl -s "http://localhost:8080/api/conflicts?page=1&page_size=10" | python -m json.tool
```

Expected: HTTP 200 with paginated conflict records (may be empty list).

## 5) Verify 404 error shape

```bash
curl -s http://localhost:8080/api/runs/nonexistent-run-id | python -m json.tool
```

Expected:
```json
{
  "code": "not_found",
  "message": "Ingestion run 'nonexistent-run-id' was not found.",
  "details": null,
  "correlation_id": null
}
```

## 6) Access the interactive API documentation

Open in a browser: `http://localhost:8080/docs`

Expected: FastAPI Swagger UI loads showing all Phase 1 endpoints.

## 7) Access the OpenAPI schema

```bash
curl -s http://localhost:8080/openapi.json | python -m json.tool | head -40
```

Expected: Full OpenAPI 3.x schema JSON.

## 8) Run all backend quality gates

```bash
uv run --project apps/backend ruff check apps/backend
uv run --project apps/backend ruff format --check apps/backend
uv run --project apps/backend ty check apps/backend
uv run --project apps/backend pytest apps/backend/tests
```

Expected: All gates pass with ≥90% coverage.

## 9) Start via Docker Compose local stack

```bash
docker compose up -d
docker compose ps
```

Expected: All services (`db`, `backend`, `pipeline`, `frontend`, `dagit`) report healthy status.

Verify backend via compose:
```bash
curl -s http://localhost:8080/health
```

## 10) Run affected Nx quality targets

```bash
pnpm run affected:lint
pnpm run affected:format
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
```

Expected: All affected targets pass.
