# Quickstart: Dataset Discovery Backend API

## Objective

Validate discovery and detail backend read behavior for search, recent updates, full catalog browsing, and dataset detail observation retrieval.

## Prerequisites

- Repository dependencies installed (`pnpm install`).
- Python environments synced for backend and pipeline projects.
- Local Docker Compose services available.
- Feature branch `017-dataset-discovery-api` checked out.

## 1) Start local stack and confirm database readiness

```bash
docker compose up -d
bash tools/quality/local-stack/test-db-readiness.sh
```

Expected:

- Database container is healthy.
- Readiness script reports success.

## 2) Apply database migrations

```bash
bash tools/quality/local-stack/run-db-migrations.sh
bash tools/quality/local-stack/check-db-revision.sh
```

Expected:

- Migration command succeeds.
- Reported head revision matches repository expectations.

## 3) Run backend quality checks for affected scope

```bash
uv run --project apps/backend ruff check apps/backend
uv run --project apps/backend ruff format --check apps/backend
uv run --project apps/backend ty check apps/backend
uv run --project apps/backend pytest apps/backend/tests
```

Expected:

- Lint, format, type checks, and tests pass.
- Coverage in affected backend scope remains at or above repository threshold.

## 4) Validate discovery and detail contract behavior

Run or add contract/integration tests covering:

- Search matches title/description/geographic scope/tags.
- Recent feed returns <= 5 datasets sorted by recency.
- Catalog supports search + source filtering + deterministic pagination.
- Detail returns metadata and chronological observations.
- Unknown dataset id returns explicit not-found behavior.

Expected:

- All contract assertions pass with deterministic ordering.
- Edge cases produce documented empty/not-found outcomes.

## 5) Run affected workspace checks

```bash
pnpm run affected:lint
pnpm run affected:format
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
```

Expected:

- All affected quality gates pass with no suppression or bypass changes.

## Acceptance Evidence Checklist

- Local stack and DB migration checks pass.
- Backend quality commands pass.
- Discovery and detail contract tests pass for all required surfaces.
- Deterministic ordering and pagination behavior verified.
- Not-found and empty-data semantics verified.

## Execution Evidence (2026-03-23)

Validation commands executed:

- `uv run --project apps/backend ruff check apps/backend`
  - Result: passed
- `uv run --project apps/backend ruff format --check apps/backend`
  - Result: passed
- `uv run --project apps/backend ty check apps/backend`
  - Result: passed
- `uv run --project apps/backend pytest apps/backend/tests`
  - Result: `52 passed`, backend coverage `96.22%`
- `pnpm run affected:lint`
  - Result: passed
- `pnpm run affected:format`
  - Result: passed
- `pnpm run affected:typecheck`
  - Result: passed
- `pnpm run affected:test`
  - Result: passed
- `pnpm run affected:coverage`
  - Result: passed
